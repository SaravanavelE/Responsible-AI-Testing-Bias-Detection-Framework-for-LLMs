"""PDF/HTML report generation engine."""
from datetime import datetime, timezone
from jinja2 import Template

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <style>
    body { font-family: 'Segoe UI', sans-serif; margin: 40px; color: #1a1a2e; }
    h1 { color: #0f3460; border-bottom: 3px solid #e94560; padding-bottom: 10px; }
    .score { font-size: 48px; font-weight: bold; color: {{ score_color }}; }
    .severity-critical { color: #e94560; }
    .severity-high { color: #f39c12; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    th { background: #16213e; color: white; }
    .summary { background: #f8f9fa; padding: 20px; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>{{ title }}</h1>
  <p>Generated: {{ generated_at }} | Scan: {{ scan_id }}</p>
  <div class="summary">
    <h2>Executive Summary</h2>
    <p>{{ executive_summary }}</p>
    <p class="score">{{ security_score }}/100</p>
    <p>Security Posture Score</p>
  </div>
  <h2>Risk Overview</h2>
  <ul>
    <li>Total Probes: {{ total_probes }}</li>
    <li>Failed: {{ failed_probes }}</li>
    <li>Passed: {{ passed_probes }}</li>
    <li>Vulnerabilities: {{ vulnerabilities }}</li>
  </ul>
  <h2>Top Findings</h2>
  <table>
    <tr><th>Probe</th><th>Category</th><th>Severity</th><th>Detection</th></tr>
    {% for f in findings %}
    <tr>
      <td>{{ f.probe_name }}</td>
      <td>{{ f.probe_category }}</td>
      <td class="severity-{{ f.severity }}">{{ f.severity }}</td>
      <td>{{ f.detection_type or 'N/A' }}</td>
    </tr>
    {% endfor %}
  </table>
  <h2>Compliance Mapping</h2>
  <ul>
  {% for m in compliance_items %}
    <li>{{ m.framework }} — {{ m.control_id }}: {{ m.control_name }}</li>
  {% endfor %}
  </ul>
  <h2>Recommendations</h2>
  <ol>
  {% for r in recommendations %}
    <li>{{ r }}</li>
  {% endfor %}
  </ol>
</body>
</html>
"""


class ReportGenerator:
    def __init__(self, session):
        self.session = session

    def generate(self, report):
        from app.models.scan import Scan, ProbeResult

        scan = None
        findings = []
        if report.scan_id:
            scan = self.session.query(Scan).filter(Scan.id == report.scan_id).first()
            if scan:
                findings = (
                    self.session.query(ProbeResult)
                    .filter(ProbeResult.scan_id == scan.id, ProbeResult.passed == False)
                    .limit(50)
                    .all()
                )

        compliance_items = []
        recommendations = set()
        for f in findings:
            for m in f.compliance_mappings or []:
                compliance_items.append(m)
            for r in f.recommendations or []:
                recommendations.add(r)

        score = scan.security_score if scan else 0
        score_color = "#27ae60" if score >= 80 else "#f39c12" if score >= 60 else "#e94560"

        ctx = {
            "title": report.title,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scan_id": scan.scan_id if scan else "N/A",
            "executive_summary": self._executive_summary(report.report_type, scan),
            "security_score": score,
            "score_color": score_color,
            "total_probes": scan.total_probes if scan else 0,
            "failed_probes": scan.failed_probes if scan else 0,
            "passed_probes": scan.passed_probes if scan else 0,
            "vulnerabilities": scan.vulnerabilities_count if scan else 0,
            "findings": findings,
            "compliance_items": compliance_items[:30],
            "recommendations": list(recommendations)[:15] or ["Enable live prompt firewall.", "Run weekly vulnerability scans."],
        }

        html = Template(REPORT_TEMPLATE).render(**ctx)
        report.html_content = html
        report.status = "completed"
        report.completed_at = datetime.now(timezone.utc)
        report.report_metadata = {"format": "html", "findings_count": len(findings)}

        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html).write_pdf()
            report.report_metadata["pdf_size"] = len(pdf_bytes)
            self._upload_pdf(report, pdf_bytes)
        except Exception:
            report.report_metadata["pdf_error"] = "WeasyPrint unavailable — HTML report saved"

    def _executive_summary(self, report_type: str, scan) -> str:
        if not scan:
            return f"This {report_type} report provides an overview of AI security posture."
        return (
            f"Security assessment completed with score {scan.security_score}/100. "
            f"{scan.failed_probes} of {scan.total_probes} probes failed, indicating "
            f"{scan.vulnerabilities_count} potential vulnerabilities requiring remediation."
        )

    def _upload_pdf(self, report, pdf_bytes: bytes):
        try:
            import boto3
            from app.core.config import get_settings
            settings = get_settings()
            client = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                region_name=settings.s3_region,
            )
            key = f"reports/{report.id}.pdf"
            client.put_object(Bucket=settings.s3_bucket, Key=key, Body=pdf_bytes, ContentType="application/pdf")
            report.s3_key = key
        except Exception:
            pass
