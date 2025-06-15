# src/encryption.py
import logging
from typing import Optional
from encryption_manager import EncryptionManager

logger = logging.getLogger(__name__)

# Global encryption manager instance
_encryption_manager = EncryptionManager()

def encrypt_message(text: str) -> Optional[str]:
    """Encrypt a message using the global encryption manager"""
    try:
        if not text:
            return None
        encrypted_bytes = _encryption_manager.encrypt(text)
        # Convert bytes to string for storage
        return encrypted_bytes.hex()
    except Exception as e:
        logger.error(f"Error encrypting message: {e}")
        return None

def decrypt_message(encrypted_hex: str) -> Optional[str]:
    """Decrypt a message using the global encryption manager"""
    try:
        if not encrypted_hex:
            return None
        # Convert hex string back to bytes
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        return _encryption_manager.decrypt(encrypted_bytes)
    except Exception as e:
        logger.error(f"Error decrypting message: {e}")
        return None

def rotate_encryption_key():
    """Rotate the encryption key"""
    try:
        _encryption_manager.rotate_key()
        logger.info("Encryption key rotated successfully")
    except Exception as e:
        logger.error(f"Error rotating encryption key: {e}")