"""PII redaction engine tests."""
import pytest
from app.engines.pii import PIIRedactionEngine, PIIAction


SENSITIVE_SAMPLES = [
    ("Contact me at john.doe@corp.com", "email"),
    ("SSN: 123-45-6789", "ssn"),
    ("Card: 4111-1111-1111-1111", "credit_card"),
    ("Key: sk-abcdefghijklmnopqrstuvwxyz123456", "api_key"),
]


class TestPIIEngine:
    @pytest.mark.parametrize("text,expected_type", SENSITIVE_SAMPLES)
    def test_detects_pii(self, text, expected_type):
        engine = PIIRedactionEngine()
        result = engine.scan(text)
        assert len(result.matches) >= 1
        assert any(m.type == expected_type for m in result.matches)

    def test_redacts_email(self):
        engine = PIIRedactionEngine(default_action=PIIAction.REDACT)
        result = engine.scan("Email: test@example.com")
        assert "[REDACTED:EMAIL]" in result.redacted_text
        assert "test@example.com" not in result.redacted_text

    def test_custom_regex(self):
        engine = PIIRedactionEngine(custom_patterns=[{"name": "employee_id", "pattern": r"EMP-\d{6}"}])
        result = engine.scan("ID: EMP-123456")
        assert len(result.matches) == 1
