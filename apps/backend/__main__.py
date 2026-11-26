"""Controlled bind and interruptible server; no access logs that might capture URL secrets."""

import sys
import threading

import uvicorn
from pydantic import ValidationError

from apps.backend.main import create_app
from core.config import Settings


def main():
    try:
        settings = Settings()
    except (ValidationError, ValueError):
        print("Invalid LGS configuration. Check .env and LGS_* variables.", file=sys.stderr)
        return 2
    server = uvicorn.Server(
        uvicorn.Config(
            create_app(settings),
            host=settings.backend_host,
            port=settings.backend_port,
            access_log=False,
            log_level="warning",
        )
    )
    if "--supervised" in sys.argv:

        def control():
            # Private stdin pipe: parent close/crash (EOF) also shuts down the owned backend.
            for line in sys.stdin:
                if line.strip() == "STOP":
                    break
            server.should_exit = True

        threading.Thread(target=control, daemon=True).start()
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
