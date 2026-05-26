"""Compliance auto-mapper — OWASP, NIST, ISO, GDPR, CERT-In."""
from typing import List

COMPLIANCE_FRAMEWORKS = {
    "owasp_llm": {
        "LLM01": "Prompt Injection",
        "LLM02": "Insecure Output Handling",
        "LLM03": "Training Data Poisoning",
        "LLM04": "Model Denial of Service",
        "LLM05": "Supply Chain Vulnerabilities",
        "LLM06": "Sensitive Information Disclosure",
        "LLM07": "Insecure Plugin Design",
        "LLM08": "Excessive Agency",
        "LLM09": "Overreliance",
        "LLM10": "Model Theft",
    },
    "nist_ai_rmf": {
        "GOVERN-1": "Policies for AI risk management",
        "MAP-1": "Context of AI system established",
        "MEASURE-2": "AI risks analyzed and documented",
        "MANAGE-1": "AI risks prioritized and treated",
    },
    "iso_42001": {"A.5.2": "AI system impact assessment", "A.6.1": "AI risk treatment"},
    "gdpr": {"Art.25": "Data protection by design", "Art.32": "Security of processing", "Art.35": "DPIA"},
    "cert_in": {"CI-LLM-01": "Prompt security controls", "CI-LLM-02": "Data leakage prevention"},
    "hipaa": {"164.312": "Technical safeguards"},
    "pci_dss": {"Req 3": "Protect stored cardholder data"},
    "mitre_atlas": {"AML.T0051": "LLM Prompt Injection", "AML.T0054": "LLM Jailbreak"},
}

DETECTION_TO_COMPLIANCE = {
    "direct_prompt_injection": [
        ("owasp_llm", "LLM01"), ("nist_ai_rmf", "MANAGE-1"), ("cert_in", "CI-LLM-01"), ("mitre_atlas", "AML.T0051")
    ],
    "jailbreak": [("owasp_llm", "LLM01"), ("mitre_atlas", "AML.T0054"), ("cert_in", "CI-LLM-01")],
    "data_leakage": [("owasp_llm", "LLM06"), ("gdpr", "Art.32"), ("hipaa", "164.312"), ("cert_in", "CI-LLM-02")],
    "tool_call_abuse": [("owasp_llm", "LLM07"), ("owasp_llm", "LLM08")],
    "unsafe_output": [("owasp_llm", "LLM02")],
    "system_prompt_extraction": [("owasp_llm", "LLM01"), ("owasp_llm", "LLM10")],
    "agent_hijacking": [("owasp_llm", "LLM08")],
    "rag_manipulation": [("owasp_llm", "LLM03")],
}


def map_detection_to_compliance(detection_type: str) -> List[dict]:
    mappings = []
    key = detection_type.replace("-", "_") if detection_type else ""
    for framework, control_id in DETECTION_TO_COMPLIANCE.get(key, []):
        controls = COMPLIANCE_FRAMEWORKS.get(framework, {})
        mappings.append({
            "framework": framework,
            "control_id": control_id,
            "control_name": controls.get(control_id, control_id),
            "detection_type": detection_type,
        })
    return mappings
