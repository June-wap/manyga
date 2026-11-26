"""UTF-8 rotating JSONL logs; redaction happens after formatting, including tracebacks."""

import json
import logging
import re
import sys
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

SENSITIVE = re.compile(r"token|secret|password|authorization|cookie|api[_-]?key", re.IGNORECASE)
ASSIGNMENT = re.compile(
    r"""(?i)((?:[\w-]*(?:token|secret|password|authorization|cookie|api[_-]?key)[\w-]*)["']?\s*[:=]\s*)(?:Bearer\s+)?(?:"[^"\n]*"|'[^'\n]*'|[^\s,;\n}]+)"""
)
SENSITIVE_HEADER = re.compile(
    r"(?im)(\b(?:authorization|(?:set[-_])?cookie)\b[\"']?\s*[:=]\s*)[^\r\n]+"
)


def redact(value, secrets=()):
    if isinstance(value, dict):
        return {
            str(k): "[REDACTED]" if SENSITIVE.search(str(k)) else redact(v, secrets)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(v, secrets) for v in value]
    text = str(value)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    text = SENSITIVE_HEADER.sub(r"\1[REDACTED]", text)
    text = re.sub(r"(?i)Bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]", text)
    return ASSIGNMENT.sub(r"\1[REDACTED]", text)


class SafeFormatter(logging.Formatter):
    def __init__(self, secrets=(), jsonl=True):
        super().__init__()
        self.secrets = secrets
        self.jsonl = jsonl

    def format(self, record):
        message = (
            redact(record.msg, self.secrets)
            if isinstance(record.msg, dict)
            else redact(record.getMessage(), self.secrets)
        )
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": message,
        }
        if record.exc_info:
            entry["exception"] = redact(self.formatException(record.exc_info), self.secrets)
        return json.dumps(entry, ensure_ascii=False, default=str)


def configure_logging(directory: Path, secrets=()) -> logging.Logger:
    directory.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("lgs")
    close_logging()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    file = RotatingFileHandler(
        directory / "studio.jsonl", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    console = logging.StreamHandler()
    for handler in (file, console):
        handler.setFormatter(SafeFormatter(secrets))
        logger.addHandler(handler)
    # Uvicorn re-logs uncaught ASGI exceptions after sending the safe 500 response.
    # Its existing console handlers must use the same registered-secret redaction.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        for handler in logging.getLogger(name).handlers:
            handler.setFormatter(SafeFormatter(secrets))
    return logger


def close_logging():
    logger = logging.getLogger("lgs")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
