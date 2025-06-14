# src/encryption_manager.py
import logging
from cryptography.fernet import Fernet
logger = logging.getLogger(__name__)

class EncryptionManager:
    """Manages the VOLATILE encryption key for in-memory message logs."""
    def __init__(self):
        self._key = Fernet.generate_key()
        self._fernet = Fernet(self._key)
        logger.info("Volatile encryption manager initialized.")
    def rotate_key(self):
        logger.info("Rotating volatile encryption key for message log.")
        self._key = Fernet.generate_key(); self._fernet = Fernet(self._key)
    def encrypt(self, text: str) -> bytes: return self._fernet.encrypt(text.encode('utf-8'))
    def decrypt(self, token: bytes) -> str: return self._fernet.decrypt(token).decode('utf-8')