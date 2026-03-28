import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import json
from typing import Any, Dict
import hmac

class SecurityManager:
    def __init__(self):
        # Generate or load encryption key
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
        
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create new one"""
        key_file = "encryption.key"
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage (one-way)"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_data_integrity(self, data: str, expected_hash: str) -> bool:
        """Verify data integrity using HMAC"""
        computed_hash = self.hash_sensitive_data(data)
        return hmac.compare_digest(computed_hash, expected_hash)
    
    def encrypt_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt patient sensitive information"""
        sensitive_fields = ["name", "email", "phone", "address"]
        
        encrypted_data = patient_data.copy()
        for field in sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = self.encrypt_data(str(encrypted_data[field]))
        
        # Add integrity hash
        data_string = json.dumps(patient_data, sort_keys=True)
        encrypted_data["integrity_hash"] = self.hash_sensitive_data(data_string)
        
        return encrypted_data
    
    def decrypt_patient_data(self, encrypted_patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt patient sensitive information"""
        sensitive_fields = ["name", "email", "phone", "address"]
        
        decrypted_data = encrypted_patient_data.copy()
        for field in sensitive_fields:
            if field in decrypted_data:
                try:
                    decrypted_data[field] = self.decrypt_data(str(decrypted_data[field]))
                except Exception:
                    # If decryption fails, keep original
                    pass
        
        return decrypted_data
    
    def generate_session_token(self, user_id: str) -> str:
        """Generate secure session token"""
        timestamp = str(int(os.times()[4]))
        token_data = f"{user_id}:{timestamp}"
        return self.encrypt_data(token_data)
    
    def validate_session_token(self, token: str) -> bool:
        """Validate session token"""
        try:
            decrypted = self.decrypt_data(token)
            # Basic validation - in production, check timestamp expiry
            return ":" in decrypted
        except Exception:
            return False

# Mock encryption for demonstration (simplified version)
class MockSecurityManager:
    """Simplified security for demo purposes"""
    
    @staticmethod
    def encrypt_data(data: str) -> str:
        """Mock encryption - just base64 encode"""
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Mock decryption - just base64 decode"""
        try:
            return base64.b64decode(encrypted_data.encode()).decode()
        except Exception:
            return encrypted_data
    
    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """Simple hash for demo"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def encrypt_patient_data(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock patient data encryption"""
        sensitive_fields = ["name", "email", "phone", "address"]
        
        encrypted_data = patient_data.copy()
        for field in sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = MockSecurityManager.encrypt_data(str(encrypted_data[field]))
        
        # Add mock integrity hash
        data_string = json.dumps(patient_data, sort_keys=True)
        encrypted_data["integrity_hash"] = MockSecurityManager.hash_sensitive_data(data_string)
        
        return encrypted_data
    
    @staticmethod
    def decrypt_patient_data(encrypted_patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock patient data decryption"""
        sensitive_fields = ["name", "email", "phone", "address"]
        
        decrypted_data = encrypted_patient_data.copy()
        for field in sensitive_fields:
            if field in decrypted_data:
                try:
                    decrypted_data[field] = MockSecurityManager.decrypt_data(str(decrypted_data[field]))
                except Exception:
                    pass
        
        return decrypted_data

# Use mock security for the prototype
security_manager = MockSecurityManager()
