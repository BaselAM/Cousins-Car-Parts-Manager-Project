"""
Secure API key management for OpenAI integration.
"""

import os
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet

from logger import get_logger

# Get a module-specific logger
logger = get_logger(__name__)


class ApiKeyManager:
    """Manages secure storage and retrieval of API keys using machine-specific encryption"""

    def __init__(self, config_dir_name=".app_config", key_filename="api_key.dat"):
        """Initialize the key manager with configurable storage location"""
        # Create directory for storing API key if it doesn't exist
        self.config_dir = Path.home() / config_dir_name
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / key_filename

        # Generate encryption key based on machine-specific information
        machine_id = self._get_machine_id()
        self.encryption_key = base64.urlsafe_b64encode(hashlib.sha256(machine_id.encode()).digest())
        self.cipher = Fernet(self.encryption_key)

    def _get_machine_id(self):
        """Get a unique machine identifier for encryption"""
        try:
            if os.name == 'nt':  # Windows
                import winreg
                reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                return machine_guid
            else:  # Linux/Mac
                try:
                    # Try machine-id first
                    with open('/etc/machine-id', 'r') as f:
                        return f.read().strip()
                except FileNotFoundError:
                    # Fall back to dbus machine id on some Linux distributions
                    try:
                        with open('/var/lib/dbus/machine-id', 'r') as f:
                            return f.read().strip()
                    except FileNotFoundError:
                        # Last resort - username + hostname
                        return f"{os.getlogin()}-{os.uname().nodename}"
        except Exception as e:
            logger.error(f"Error getting machine ID, using fallback: {e}")
            # Fallback to username + hostname if we can't get a system ID
            return f"{os.getlogin()}-{os.uname().nodename}"

    def save_api_key(self, api_key):
        """Encrypt and save the API key"""
        try:
            # Encrypt the API key
            encrypted_key = self.cipher.encrypt(api_key.encode())

            # Save to file with secure permissions
            with open(self.key_file, 'wb') as f:
                f.write(encrypted_key)

            # Set file permissions (on Unix systems)
            try:
                if os.name != 'nt':  # Not Windows
                    os.chmod(self.key_file, 0o600)  # Read/write only for user
            except Exception as e:
                logger.warning(f"Could not set file permissions: {e}")

            logger.info("API key saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving API key: {e}")
            return False

    def load_api_key(self):
        """Load and decrypt the API key"""
        try:
            if not self.key_file.exists():
                logger.debug("No API key file found")
                return None

            # Read encrypted key
            with open(self.key_file, 'rb') as f:
                encrypted_key = f.read()

            # Decrypt and return
            api_key = self.cipher.decrypt(encrypted_key).decode()
            logger.info("API key loaded successfully")
            return api_key
        except Exception as e:
            logger.error(f"Error loading API key: {e}")
            # If there's a decryption error, try to clean up the potentially corrupted file
            if "token" in str(e).lower() or "decrypt" in str(e).lower():
                self.delete_api_key()
            return None

    def delete_api_key(self):
        """Delete the stored API key"""
        try:
            if self.key_file.exists():
                self.key_file.unlink()
                logger.info("API key deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting API key: {e}")
            return False