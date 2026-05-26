"""Scan execution orchestrator."""
import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Callable, Optional

from app.data.scan_suites import SUITE_BY_ID, ProbeDefinition
from app.engines.compliance import map_detection_to_compliance
from app.engines.detection import detection_engine
from app.engines.dynamic_probes import dynamic_probe_generator
from app.engines.llm_client import LLMClient


def generate_scan_id() -> str:
    return f"SCN-{uuid.uuid4().hex[:12].upper()}"


def calculate_security_score(passed: int, total: int, avg_risk: float) -> float:
    if total == 0:
        return 100.0
    pass_rate = passed / total
    risk_penalty = min(avg_risk * 40, 40)
    return max(0.0, min(100.0, round(pass_rate * 100 - risk_penalty, 2)))


class ScanExecutor:
    def __init__(self, connection: dict, log_callback: Optional[Callable] = None):
        self.client = LLMClient(connection)
        self.log = log_callback or (lambda msg, level="info": None)

    def collect_probes(
        self,
        suite_ids: list[str],
        dynamic_suites: list[str],
        scan_id: str = "",
    ) -> list[ProbeDefinition]:
        probes: list[ProbeDefinition] = []
        for sid in suite_ids:
            suite = SUITE_BY_ID.get(sid)
            if suite:
                for p in suite.probes:
                    probes.append(p)
        for ds in dynamic_suites:
            probes.extend(dynamic_probe_generator.generate(ds, {"scan_id": scan_id}))
        return probes

    async def run_probe(self, probe: ProbeDefinition, suite_name: str) -> dict:
        start = time.perf_counter()
        self.log(f"Running probe: {probe.name}", "info")
        try:
            response, raw = await self.client.complete(probe.prompt)
        except Exception as e:
            return {
                "probe_name": probe.name,
                "probe_category": probe.category,
                "suite": suite_name,
                "severity": probe.severity,
                "status": "error",
                "passed": False,
                "prompt": probe.prompt,
                "response": str(e),
                "detection_type": "connection_error",
                "risk_score": 0.5,
                "evidence": {"error": str(e)},
                "compliance_mappings": [],
                "recommendations": ["Verify LLM connection credentials and endpoint."],
                "duration_ms": int((time.perf_counter() - start) * 1000),
            }

        detection = detection_engine.analyze(probe.prompt, response, probe.category)
        passed = not detection.detected
        detection_type = detection.detection_type.value if detection.detection_type else None
        compliance = map_detection_to_compliance(detection_type or "") if detection.detected else []
        recommendations = []
        if not passed:
            recommendations = [
                f"Implement guardrails for {detection_type or probe.category}.",
                "Add input/output filtering in the prompt firewall.",
                "Review system prompt isolation and tool permissions.",
            ]

        return {
            "probe_name": probe.name,
            "probe_category": probe.category,
            "suite": suite_name,
            "severity": probe.severity,
            "status": "passed" if passed else "failed",
            "passed": passed,
            "prompt": probe.prompt[:4000],
            "response": response[:8000] if response else "",
            "detection_type": detection_type,
            "risk_score": detection.risk_score if detection.detected else 0.0,
            "evidence": detection.evidence,
            "compliance_mappings": compliance,
            "recommendations": recommendations,
            "duration_ms": int((time.perf_counter() - start) * 1000),
        }

    async def execute(
        self,
        suite_ids: list[str],
        dynamic_suites: list[str],
        parallelism: int = 4,
        scan_id: str = "",
    ) -> AsyncGenerator[dict, None]:
        probes = self.collect_probes(suite_ids, dynamic_suites, scan_id)
        yield {"type": "init", "total_probes": len(probes)}

        semaphore = asyncio.Semaphore(parallelism)
        completed = 0
        passed = 0
        failed = 0
        risks: list[float] = []

        async def run_with_sem(probe: ProbeDefinition, suite: str):
            nonlocal completed, passed, failed
            async with semaphore:
                suite_name = next((s.name for s in SUITE_BY_ID.values() if probe in s.probes), probe.category)
                result = await self.run_probe(probe, suite_name or probe.category)
                completed += 1
                if result["passed"]:
                    passed += 1
                else:
                    failed += 1
                    risks.append(result["risk_score"])
                yield_result = {
                    "type": "probe_complete",
                    "completed": completed,
                    "total": len(probes),
                    "passed": passed,
                    "failed": failed,
                    "security_score": calculate_security_score(passed, completed, sum(risks) / max(len(risks), 1)),
                    "result": result,
                }
                return yield_result

        tasks = []
        for probe in probes:
            suite_name = probe.category
            for sid in suite_ids:
                if sid in SUITE_BY_ID and probe in SUITE_BY_ID[sid].probes:
                    suite_name = SUITE_BY_ID[sid].name
                    break

            async def wrapped(p=probe, s=suite_name):
                async with semaphore:
                    return await self.run_probe(p, s)

            tasks.append(wrapped())

        for coro in asyncio.as_completed(tasks):
            result = await coro
            completed_count = passed + failed
            if result["passed"]:
                passed += 1
            else:
                failed += 1
                risks.append(result["risk_score"])
            yield {
                "type": "probe_complete",
                "completed": completed_count,
                "total": len(probes),
                "passed": passed,
                "failed": failed,
                "security_score": calculate_security_score(passed, completed_count, sum(risks) / max(len(risks), 1)),
                "result": result,
            }

        avg_risk = sum(risks) / max(len(risks), 1)
        yield {
            "type": "complete",
            "total_probes": len(probes),
            "passed_probes": passed,
            "failed_probes": failed,
            "security_score": calculate_security_score(passed, len(probes), avg_risk),
            "risk_score": round(avg_risk * 100, 2),
            "vulnerabilities_count": failed,
        }
