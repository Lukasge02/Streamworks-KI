"""
Secure Configuration Management for StreamWorks-KI
Implements enterprise-grade secret management and security hardening
"""
import base64
import hashlib
import logging
import os
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    logger.warning("cryptography package not available - using fallback security")
    CRYPTOGRAPHY_AVAILABLE = False
    Fernet = None
    hashes = None
    PBKDF2HMAC = None


class SecretManager:
    """Enterprise-grade secret management system"""
    
    def __init__(self):
        self._encryption_key: Optional[bytes] = None
        self._secrets_cache: Dict[str, str] = {}
        self._initialized = False
    
    def initialize(self, master_password: Optional[str] = None) -> None:
        """Initialize secret manager with encryption key"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                logger.warning("🔒 Cryptography not available - using fallback mode")
                self._encryption_key = b"fallback_key_dev_only"
                self._initialized = True
                return
                
            # Generate or load encryption key
            key_file = Path(".secrets_key")
            
            if key_file.exists() and master_password:
                # Load existing key with password
                self._encryption_key = self._derive_key_from_password(master_password)
                logger.info("🔐 Secret manager initialized with existing key")
            else:
                # Generate new key for first-time setup
                if CRYPTOGRAPHY_AVAILABLE and Fernet is not None:
                    self._encryption_key = Fernet.generate_key()
                    if not key_file.exists():
                        # Save key (in production, use proper key management service)
                        with open(key_file, "wb") as f:
                            f.write(self._encryption_key)
                        logger.info("🔑 New encryption key generated and saved")
                else:
                    # Fallback for development
                    self._encryption_key = b"fallback_key_dev_only"
                    logger.warning("🔒 Using fallback encryption key")
                    
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize secret manager: {e}")
            # Fallback to basic mode for development
            logger.warning("🔒 Using fallback security mode")
            self._encryption_key = b"fallback_key_dev_only"
            self._initialized = True
    
    def _derive_key_from_password(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        if not CRYPTOGRAPHY_AVAILABLE:
            # Fallback to simple hash for development
            return hashlib.sha256(password.encode()).digest()
            
        salt = b"streamworks_ki_salt_2024"  # In production: use random salt per installation
        if PBKDF2HMAC is not None and hashes is not None:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            # Fallback for when cryptography is not available
            return hashlib.sha256(password.encode() + salt).digest()
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt a secret value"""
        if not self._initialized:
            raise SecurityError("Secret manager not initialized")
        
        if not CRYPTOGRAPHY_AVAILABLE or Fernet is None or self._encryption_key is None:
            # Fallback to base64 encoding for development
            return base64.urlsafe_b64encode(secret.encode()).decode()
            
        fernet = Fernet(self._encryption_key)
        encrypted = fernet.encrypt(secret.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt a secret value"""
        if not self._initialized:
            raise SecurityError("Secret manager not initialized")
        
        try:
            if not CRYPTOGRAPHY_AVAILABLE or Fernet is None or self._encryption_key is None:
                # Fallback to base64 decoding for development
                return base64.urlsafe_b64decode(encrypted_secret.encode()).decode()
                
            fernet = Fernet(self._encryption_key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_secret.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"❌ Failed to decrypt secret: {e}")
            raise SecurityError("Secret decryption failed")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment or cache"""
        # Check cache first
        if key in self._secrets_cache:
            return self._secrets_cache[key]
        
        # Check environment variable
        env_value = os.getenv(key)
        if env_value:
            # Check if encrypted (starts with specific prefix)
            if env_value.startswith("ENCRYPTED:"):
                try:
                    decrypted = self.decrypt_secret(env_value[10:])  # Remove "ENCRYPTED:" prefix
                    self._secrets_cache[key] = decrypted
                    return decrypted
                except Exception as e:
                    logger.error(f"❌ Failed to decrypt environment secret {key}: {e}")
                    return default
            else:
                # Plain text environment variable
                self._secrets_cache[key] = env_value
                return env_value
        
        return default
    
    def set_secret(self, key: str, value: str, encrypt: bool = True) -> None:
        """Set a secret value"""
        if encrypt and self._initialized:
            encrypted_value = self.encrypt_secret(value)
            os.environ[key] = f"ENCRYPTED:{encrypted_value}"
        else:
            os.environ[key] = value
        
        self._secrets_cache[key] = value


class SecurityError(Exception):
    """Security-related errors"""
    pass


class SecureConfigValidator:
    """Validates configuration for security compliance"""
    
    @staticmethod
    def validate_secret_key(secret_key: str) -> bool:
        """Validate secret key strength"""
        if not secret_key or len(secret_key) < 32:
            return False
        
        # Check for common weak keys
        weak_keys = [
            "dev-secret-key-change-in-production",
            "your-secret-key-here",
            "change-me",
            "secret",
            "password",
            "test"
        ]
        
        if secret_key.lower() in [key.lower() for key in weak_keys]:
            return False
        
        return True
    
    @staticmethod
    def validate_database_url(db_url: str, environment: str) -> bool:
        """Validate database URL security"""
        if environment == "production":
            # Production databases must use SSL
            if "postgresql://" in db_url and "sslmode=" not in db_url:
                logger.warning("⚠️ Production database should use SSL")
                return False
            
            # No SQLite in production
            if db_url.startswith("sqlite:"):
                logger.error("❌ SQLite not allowed in production")
                return False
        
        return True
    
    @staticmethod
    def validate_cors_origins(origins: Optional[List[str]], environment: str) -> bool:
        """Validate CORS origins"""
        if not origins:
            return True
            
        if environment == "production":
            # No localhost in production CORS
            for origin in origins:
                if "localhost" in origin or "127.0.0.1" in origin:
                    logger.warning(f"⚠️ Localhost CORS origin in production: {origin}")
                    return False
        
        return True


class ProductionSecrets:
    """Secure secret generation for production"""
    
    @staticmethod
    def generate_secret_key() -> str:
        """Generate cryptographically secure secret key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_database_password() -> str:
        """Generate secure database password"""
        return secrets.token_urlsafe(24)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return f"sk-{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password securely"""
        salt = secrets.token_bytes(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + pwdhash.hex()
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt = bytes.fromhex(stored_hash[:64])
            stored_pwdhash = bytes.fromhex(stored_hash[64:])
            pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return pwdhash == stored_pwdhash
        except Exception:
            return False


# Global secret manager instance
secret_manager = SecretManager()


def initialize_security(master_password: Optional[str] = None) -> None:
    """Initialize security subsystem"""
    try:
        secret_manager.initialize(master_password)
        logger.info("🔐 Security subsystem initialized")
    except Exception as e:
        logger.error(f"❌ Security initialization failed: {e}")
        raise


def get_secure_config_value(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get configuration value with security checks"""
    value = secret_manager.get_secret(key, default)
    
    if required and not value:
        raise SecurityError(f"Required secure configuration '{key}' not found")
    
    return value


def validate_production_config(config_dict: Dict[str, Any], environment: str) -> Dict[str, Any]:
    """Validate configuration for production deployment"""
    issues = []
    validator = SecureConfigValidator()
    
    # Validate secret key
    secret_key = config_dict.get("secret_key", "")
    if not validator.validate_secret_key(secret_key):
        issues.append("CRITICAL: Weak or default secret key detected")
    
    # Validate database URL
    db_url = config_dict.get("database_url", "")
    if not validator.validate_database_url(db_url, environment):
        issues.append("CRITICAL: Insecure database configuration")
    
    # Validate CORS
    cors_origins = config_dict.get("allowed_origins", [])
    if not validator.validate_cors_origins(cors_origins, environment):
        issues.append("WARNING: Insecure CORS configuration")
    
    # Check for debug mode in production
    if environment == "production" and config_dict.get("debug", False):
        issues.append("CRITICAL: Debug mode enabled in production")
    
    return {
        "is_secure": len([i for i in issues if "CRITICAL" in i]) == 0,
        "issues": issues
    }


# Security middleware functions
def mask_sensitive_data(data: str, patterns: Optional[List[str]] = None) -> str:
    """Mask sensitive data in logs/responses"""
    if patterns is None:
        patterns = [
            r'password["\s]*[:=]["\s]*([^"\s,}]+)',
            r'secret["\s]*[:=]["\s]*([^"\s,}]+)',
            r'key["\s]*[:=]["\s]*([^"\s,}]+)',
            r'token["\s]*[:=]["\s]*([^"\s,}]+)',
        ]
    
    import re
    
    masked_data = data
    for pattern in patterns:
        masked_data = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), "***MASKED***"), masked_data, flags=re.IGNORECASE)
    
    return masked_data


def secure_headers() -> Dict[str, str]:
    """Generate security headers for HTTP responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
    }