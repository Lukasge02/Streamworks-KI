"""
Security Module Unit Tests
Comprehensive testing for security features and validation
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from app.core.security import (
    SecretManager, 
    SecurityError, 
    SecureConfigValidator,
    ProductionSecrets,
    validate_production_config,
    mask_sensitive_data,
    secure_headers
)
from app.models.validation import (
    InputSanitizer,
    validate_file_upload,
    validate_user_input,
    validate_search_query,
    validate_stream_config,
    RateLimitValidator,
    UserInputModel,
    FileUploadModel,
    SearchQueryModel,
    StreamConfigModel,
    SecurityError as ValidationSecurityError
)


class TestSecretManager:
    """Test secret management functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.secret_manager = SecretManager()
    
    def test_generate_encryption_key(self):
        """Test encryption key generation"""
        self.secret_manager.initialize()
        assert self.secret_manager._encryption_key is not None
        assert len(self.secret_manager._encryption_key) > 0
    
    def test_encrypt_decrypt_secret(self):
        """Test secret encryption/decryption"""
        self.secret_manager.initialize()
        
        secret = "super-secret-password-123"
        encrypted = self.secret_manager.encrypt_secret(secret)
        decrypted = self.secret_manager.decrypt_secret(encrypted)
        
        assert encrypted != secret
        assert decrypted == secret
    
    def test_get_secret_from_env(self):
        """Test getting secrets from environment"""
        self.secret_manager.initialize()
        
        # Test plain environment variable
        os.environ["TEST_SECRET"] = "plain_value"
        assert self.secret_manager.get_secret("TEST_SECRET") == "plain_value"
        
        # Test encrypted environment variable
        encrypted_value = self.secret_manager.encrypt_secret("encrypted_value")
        os.environ["TEST_ENCRYPTED"] = f"ENCRYPTED:{encrypted_value}"
        assert self.secret_manager.get_secret("TEST_ENCRYPTED") == "encrypted_value"
        
        # Cleanup
        del os.environ["TEST_SECRET"]
        del os.environ["TEST_ENCRYPTED"]
    
    def test_secret_manager_not_initialized(self):
        """Test error when secret manager not initialized"""
        with pytest.raises(SecurityError):
            self.secret_manager.encrypt_secret("test")


class TestSecureConfigValidator:
    """Test configuration validation"""
    
    def test_validate_secret_key_strong(self):
        """Test strong secret key validation"""
        strong_key = ProductionSecrets.generate_secret_key()
        assert SecureConfigValidator.validate_secret_key(strong_key)
    
    def test_validate_secret_key_weak(self):
        """Test weak secret key rejection"""
        weak_keys = [
            "dev-secret-key-change-in-production",
            "secret",
            "password",
            "short",
            ""
        ]
        
        for weak_key in weak_keys:
            assert not SecureConfigValidator.validate_secret_key(weak_key)
    
    def test_validate_database_url_production(self):
        """Test database URL validation for production"""
        # SQLite should be rejected in production
        assert not SecureConfigValidator.validate_database_url(
            "sqlite:///test.db", "production"
        )
        
        # PostgreSQL without SSL should be rejected
        assert not SecureConfigValidator.validate_database_url(
            "postgresql://user:pass@host/db", "production"
        )
        
        # PostgreSQL with SSL should be accepted
        assert SecureConfigValidator.validate_database_url(
            "postgresql://user:pass@host/db?sslmode=require", "production"
        )
    
    def test_validate_cors_origins_production(self):
        """Test CORS origins validation for production"""
        # Localhost should be rejected in production
        localhost_origins = ["http://localhost:3000", "http://127.0.0.1:8080"]
        assert not SecureConfigValidator.validate_cors_origins(
            localhost_origins, "production"
        )
        
        # Valid production origins should be accepted
        prod_origins = ["https://streamworks.example.com"]
        assert SecureConfigValidator.validate_cors_origins(
            prod_origins, "production"
        )


class TestProductionSecrets:
    """Test production secret generation"""
    
    def test_generate_secret_key(self):
        """Test secret key generation"""
        key = ProductionSecrets.generate_secret_key()
        assert len(key) >= 32
        assert isinstance(key, str)
    
    def test_generate_api_key(self):
        """Test API key generation"""
        api_key = ProductionSecrets.generate_api_key()
        assert api_key.startswith("sk-")
        assert len(api_key) > 35
    
    def test_hash_verify_password(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = ProductionSecrets.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50
        assert ProductionSecrets.verify_password(password, hashed)
        assert not ProductionSecrets.verify_password("wrong_password", hashed)


class TestInputSanitizer:
    """Test input sanitization functionality"""
    
    def test_sanitize_html_basic(self):
        """Test basic HTML sanitization"""
        malicious_input = '<script>alert("xss")</script>Hello'
        sanitized = InputSanitizer.sanitize_html(malicious_input)
        assert '<script>' not in sanitized
        assert 'Hello' in sanitized
    
    def test_sanitize_html_with_allowed_tags(self):
        """Test HTML sanitization with allowed tags"""
        input_text = '<p>Hello <strong>world</strong></p><script>alert("xss")</script>'
        sanitized = InputSanitizer.sanitize_html(input_text, allow_tags=True)
        assert '<p>' in sanitized
        assert '<strong>' in sanitized
        assert '<script>' not in sanitized
    
    def test_dangerous_patterns_detection(self):
        """Test detection of dangerous patterns"""
        dangerous_inputs = [
            'javascript:alert("xss")',
            '<iframe src="evil.com"></iframe>',
            'eval("malicious code")',
            'document.cookie',
            'window.location',
            'onload="evil()"'
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(ValidationSecurityError):
                InputSanitizer.sanitize_html(dangerous_input)
    
    def test_sql_injection_detection(self):
        """Test SQL injection pattern detection"""
        sql_injections = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "UNION SELECT * FROM passwords",
            "admin'--",
            "; EXEC xp_cmdshell",
            "WAITFOR DELAY '00:00:05'"
        ]
        
        for sql_injection in sql_injections:
            with pytest.raises(ValidationSecurityError):
                InputSanitizer.check_sql_injection(sql_injection)
    
    def test_filename_sanitization(self):
        """Test filename sanitization"""
        dangerous_filenames = [
            "../../../etc/passwd",
            "file<script>.txt",
            'file"with"quotes.doc',
            "CON.txt",  # Windows reserved name
            "file|pipe.pdf"
        ]
        
        for dangerous_filename in dangerous_filenames:
            sanitized = InputSanitizer.sanitize_filename(dangerous_filename)
            assert '..' not in sanitized
            assert '<' not in sanitized
            assert '|' not in sanitized
            assert len(sanitized) > 0
    
    @patch('magic.from_buffer')
    def test_file_content_validation(self, mock_magic):
        """Test file content validation"""
        mock_magic.return_value = 'text/plain'
        
        # Test normal file
        content = b"This is a normal text file"
        InputSanitizer.validate_file_content(content, "test.txt")
        
        # Test oversized file
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        with pytest.raises(ValidationSecurityError):
            InputSanitizer.validate_file_content(large_content, "large.txt")
        
        # Test disallowed extension
        with pytest.raises(ValidationSecurityError):
            InputSanitizer.validate_file_content(content, "malware.exe")
    
    def test_dangerous_file_signatures(self):
        """Test detection of dangerous file signatures"""
        # Windows PE signature
        pe_content = b"MZ\x90\x00" + b"x" * 100
        with pytest.warns():  # Should log warning
            InputSanitizer.validate_file_content(pe_content, "file.txt")
        
        # ELF signature
        elf_content = b"\x7fELF" + b"x" * 100
        with pytest.warns():  # Should log warning
            InputSanitizer.validate_file_content(elf_content, "file.txt")


class TestValidationModels:
    """Test Pydantic validation models"""
    
    def test_user_input_model_valid(self):
        """Test valid user input"""
        valid_input = UserInputModel(message="Hello, how can I help you?")
        assert valid_input.message == "Hello, how can I help you?"
    
    def test_user_input_model_xss_protection(self):
        """Test XSS protection in user input"""
        malicious_input = '<script>alert("xss")</script>Hello'
        sanitized_model = UserInputModel(message=malicious_input)
        assert '<script>' not in sanitized_model.message
        assert 'Hello' in sanitized_model.message
    
    def test_file_upload_model_valid(self):
        """Test valid file upload model"""
        file_model = FileUploadModel(
            filename="test.txt",
            file_size=1024,
            content_type="text/plain"
        )
        assert file_model.filename == "test.txt"
    
    def test_file_upload_model_filename_sanitization(self):
        """Test filename sanitization in file upload"""
        dangerous_filename = "../../../malicious.txt"
        file_model = FileUploadModel(
            filename=dangerous_filename,
            file_size=1024
        )
        assert '..' not in file_model.filename
        assert 'malicious.txt' in file_model.filename
    
    def test_search_query_model_valid(self):
        """Test valid search query"""
        search_model = SearchQueryModel(
            query="StreamWorks XML configuration",
            top_k=10
        )
        assert search_model.query == "StreamWorks XML configuration"
        assert search_model.top_k == 10
    
    def test_search_query_model_sql_injection_protection(self):
        """Test SQL injection protection in search"""
        with pytest.raises(ValueError):
            SearchQueryModel(query="'; DROP TABLE users; --")
    
    def test_stream_config_model_valid(self):
        """Test valid stream configuration"""
        xml_content = '<?xml version="1.0"?><stream><name>test</name></stream>'
        stream_model = StreamConfigModel(
            stream_name="Test Stream",
            xml_content=xml_content
        )
        assert stream_model.stream_name == "Test Stream"
    
    def test_stream_config_model_xml_security(self):
        """Test XML security validation"""
        dangerous_xml = '<?xml version="1.0"?><!DOCTYPE test [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><test>&xxe;</test>'
        
        with pytest.raises(ValueError):
            StreamConfigModel(
                stream_name="Dangerous Stream",
                xml_content=dangerous_xml
            )


class TestValidationFunctions:
    """Test validation utility functions"""
    
    def test_validate_file_upload(self):
        """Test file upload validation function"""
        content = b"This is a test file"
        validated = validate_file_upload("test.txt", content, "text/plain")
        
        assert isinstance(validated, FileUploadModel)
        assert validated.filename == "test.txt"
        assert validated.file_size == len(content)
    
    def test_validate_user_input(self):
        """Test user input validation function"""
        validated = validate_user_input("Hello, world!")
        
        assert isinstance(validated, UserInputModel)
        assert validated.message == "Hello, world!"
    
    def test_validate_search_query(self):
        """Test search query validation function"""
        validated = validate_search_query("test query", 5)
        
        assert isinstance(validated, SearchQueryModel)
        assert validated.query == "test query"
        assert validated.top_k == 5
    
    def test_validate_stream_config(self):
        """Test stream configuration validation function"""
        xml_content = '<?xml version="1.0"?><stream><name>test</name></stream>'
        validated = validate_stream_config("Test Stream", xml_content, "Description")
        
        assert isinstance(validated, StreamConfigModel)
        assert validated.stream_name == "Test Stream"


class TestRateLimitValidator:
    """Test rate limiting functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.rate_limiter = RateLimitValidator()
    
    def test_rate_limit_within_bounds(self):
        """Test normal requests within rate limits"""
        client_ip = "192.168.1.1"
        endpoint = "/api/v1/chat"
        
        # Should allow requests within limit
        for i in range(5):
            assert self.rate_limiter.check_rate_limit(client_ip, endpoint, max_requests=10)
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded"""
        client_ip = "192.168.1.2"
        endpoint = "/api/v1/upload"
        max_requests = 3
        
        # Use up the limit
        for i in range(max_requests):
            assert self.rate_limiter.check_rate_limit(client_ip, endpoint, max_requests=max_requests)
        
        # Next request should be blocked
        assert not self.rate_limiter.check_rate_limit(client_ip, endpoint, max_requests=max_requests)
        assert self.rate_limiter.is_blocked(client_ip)
    
    def test_rate_limit_different_ips(self):
        """Test rate limiting is per IP"""
        endpoint = "/api/v1/test"
        max_requests = 2
        
        # First IP uses up its limit
        ip1 = "192.168.1.3"
        for i in range(max_requests):
            assert self.rate_limiter.check_rate_limit(ip1, endpoint, max_requests=max_requests)
        assert not self.rate_limiter.check_rate_limit(ip1, endpoint, max_requests=max_requests)
        
        # Second IP should still have full limit
        ip2 = "192.168.1.4"
        assert self.rate_limiter.check_rate_limit(ip2, endpoint, max_requests=max_requests)


class TestSecurityUtilities:
    """Test security utility functions"""
    
    def test_mask_sensitive_data(self):
        """Test sensitive data masking"""
        sensitive_text = 'password: "secret123", api_key: "abc123", token: "xyz789"'
        masked = mask_sensitive_data(sensitive_text)
        
        assert "secret123" not in masked
        assert "abc123" not in masked
        assert "xyz789" not in masked
        assert "***MASKED***" in masked
    
    def test_secure_headers(self):
        """Test security headers generation"""
        headers = secure_headers()
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        for header in required_headers:
            assert header in headers
            assert headers[header] is not None
    
    def test_validate_production_config(self):
        """Test production configuration validation"""
        # Valid production config
        valid_config = {
            "secret_key": ProductionSecrets.generate_secret_key(),
            "database_url": "postgresql://user:pass@host/db?sslmode=require",
            "allowed_origins": ["https://streamworks.example.com"],
            "debug": False
        }
        
        result = validate_production_config(valid_config, "production")
        assert result["is_secure"]
        assert len(result["issues"]) == 0
        
        # Invalid production config
        invalid_config = {
            "secret_key": "dev-secret-key-change-in-production",
            "database_url": "sqlite:///test.db",
            "allowed_origins": ["http://localhost:3000"],
            "debug": True
        }
        
        result = validate_production_config(invalid_config, "production")
        assert not result["is_secure"]
        assert len(result["issues"]) > 0
        assert any("CRITICAL" in issue for issue in result["issues"])


@pytest.mark.asyncio
class TestAsyncSecurity:
    """Test async security features"""
    
    async def test_async_validation_performance(self):
        """Test that validation doesn't block async operations"""
        import asyncio
        import time
        
        async def validate_multiple_inputs():
            tasks = []
            for i in range(10):
                task = asyncio.create_task(
                    asyncio.to_thread(validate_user_input, f"Test message {i}")
                )
                tasks.append(task)
            return await asyncio.gather(*tasks)
        
        start_time = time.time()
        results = await validate_multiple_inputs()
        end_time = time.time()
        
        assert len(results) == 10
        assert end_time - start_time < 1.0  # Should complete quickly
    
    async def test_file_validation_async(self):
        """Test async file validation"""
        import asyncio
        
        async def validate_file_async():
            content = b"Test file content"
            return await asyncio.to_thread(
                validate_file_upload, "test.txt", content, "text/plain"
            )
        
        result = await validate_file_async()
        assert isinstance(result, FileUploadModel)


class TestSecurityIntegration:
    """Integration tests for security components"""
    
    def test_end_to_end_file_security(self):
        """Test complete file security validation flow"""
        # Create a test file
        content = b"StreamWorks configuration data"
        filename = "config.txt"
        
        # Validate file upload
        file_model = validate_file_upload(filename, content)
        assert file_model.filename == filename
        
        # Validate content doesn't contain dangerous patterns
        content_str = content.decode('utf-8')
        sanitized = InputSanitizer.sanitize_html(content_str)
        assert sanitized == content_str  # Should be unchanged for safe content
        
        # Check no SQL injection patterns
        InputSanitizer.check_sql_injection(content_str)  # Should not raise
    
    def test_configuration_security_chain(self):
        """Test configuration security validation chain"""
        # Generate secure configuration
        config = {
            "secret_key": ProductionSecrets.generate_secret_key(),
            "database_url": "postgresql://user:pass@host/db?sslmode=require",
            "allowed_origins": ["https://streamworks.example.com"],
            "debug": False
        }
        
        # Validate each component
        assert SecureConfigValidator.validate_secret_key(config["secret_key"])
        assert SecureConfigValidator.validate_database_url(config["database_url"], "production")
        assert SecureConfigValidator.validate_cors_origins(config["allowed_origins"], "production")
        
        # Validate overall configuration
        result = validate_production_config(config, "production")
        assert result["is_secure"]
    
    def test_input_validation_chain(self):
        """Test complete input validation chain"""
        user_message = "How do I configure StreamWorks XML streams?"
        
        # Validate user input
        user_model = validate_user_input(user_message)
        assert user_model.message == user_message
        
        # Validate as search query
        search_model = validate_search_query(user_message)
        assert search_model.query == user_message
        
        # Rate limiting
        rate_limiter = RateLimitValidator()
        assert rate_limiter.check_rate_limit("192.168.1.100", "/api/v1/chat")


if __name__ == "__main__":
    pytest.main([__file__])