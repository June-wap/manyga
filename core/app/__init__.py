"""Backend lifecycle, version, paths and owned resources."""

import logging
import time

from core.config import Settings
from core.logging import close_logging, configure_logging
from core.security import SessionCredentials
from core.sqlite_smoke import run_smoke

VERSION = "0.1.0"


class ApplicationCore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.credentials = SessionCredentials()
        self.started_at = 0.0
        self.running = False
        self.db_smoke_ok = False

    def startup(self):
        secrets = (
            self.credentials.admin.get_secret_value(),
            self.credentials.renderer.get_secret_value(),
        )
        logger = configure_logging(self.settings.log_dir, secrets)
        try:
            self.settings.data_dir.mkdir(parents=True, exist_ok=True)
            self.sqlite = run_smoke(self.settings.db_path)
            self.db_smoke_ok = True
            self.started_at = time.monotonic()
            self.running = True
            logger.info("Application started (%s)", self.settings.environment)
        except Exception:
            logger.exception("Startup failed")
            close_logging()
            raise

    def shutdown(self):
        self.running = False
        logging.getLogger("lgs").info("Application shutdown")
        close_logging()
