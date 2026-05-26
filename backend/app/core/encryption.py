import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import get_settings


def _derive_fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


class SecretVault:
    """Encrypt/decrypt API keys and sensitive tenant credentials."""

    def __init__(self, key: str | None = None):
        settings = get_settings()
        raw = key or settings.encryption_key
        try:
            self._fernet = Fernet(raw.encode() if len(raw) == 44 else _derive_fernet_key(raw))
        except Exception:
            self._fernet = Fernet(_derive_fernet_key(raw))

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()


vault = SecretVault()
