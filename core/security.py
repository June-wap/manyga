"""Session credentials remain in memory. No persisted credentials or renderer API in GD01."""

import secrets
from dataclasses import dataclass, field

from pydantic import SecretStr


@dataclass(repr=False)
class SessionCredentials:
    admin: SecretStr = field(default_factory=lambda: SecretStr(secrets.token_urlsafe(32)))
    renderer: SecretStr = field(default_factory=lambda: SecretStr(secrets.token_urlsafe(32)))

    def permits_admin(self, credential: str) -> bool:
        return secrets.compare_digest(credential.encode(), self.admin.get_secret_value().encode())
