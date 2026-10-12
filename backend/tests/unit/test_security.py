import logging

from app.core.security import RedactFilter, redact_mapping, secret_registry


def test_mapping_redacts_password_keys():
    cleaned = redact_mapping({"username": "tester", "password": "super-secret", "nested": {"api_key": "abc"}})
    assert cleaned["password"] == "***"
    assert cleaned["nested"]["api_key"] == "***"
    assert cleaned["username"] == "tester"


def test_log_filter_removes_registered_secret():
    secret_registry.add("super-secret-value")
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "login super-secret-value failed", None, None)
    assert RedactFilter().filter(record)
    assert "super-secret-value" not in record.getMessage()
    secret_registry.discard("super-secret-value")
