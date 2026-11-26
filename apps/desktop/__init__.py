"""Operator shell; all database state comes from the backend API."""

# Resolve Pydantic's lazy imports before Qt 6.12 installs its module inspection hook.
# Without this order a fresh `python -m apps.desktop` can recurse into a partial module.
from core import config as _config  # noqa: F401
