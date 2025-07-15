"""
Comprehensive input validation and sanitization
"""
import re
import html
import hashlib
import mimetypes
from typing import List, Optional, Any, Dict
from pathlib import Path
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException, status, UploadFile
import magic


class SecurityValidator:
    """Security validation utilities"""
    
    # Dangerous patterns to block
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
    ]
    
    SQL_INJECTION_PATTERNS = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
        r'(\b(or|and)\s+\w+\s*=\s*\w+)',
        r'(\b(or|and)\s+\d+\s*=\s*\d+)',
        r'(\b(or|and)\s+[\'"][^\'"]*[\'"])',
        r'(--|#|/\*|\*/)',
        r'(\bxp_\w+)',
        r'(\bsp_\w+)',
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\.[/\\]',
        r'[/\\]\.\.[/\\]',
        r'^\.\./',
        r'^\.\.\\',
    ]
    
    @classmethod
    def validate_text_input(cls, text: str, field_name: str = "text") -> str:
        """Validate and sanitize text input"""
        if not isinstance(text, str):
            raise ValueError(f"{field_name} must be a string")
        
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError(f"{field_name} contains potentially dangerous content")
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError(f"{field_name} contains potentially dangerous SQL patterns")
        
        # HTML escape for safety
        sanitized = html.escape(text)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """Validate and sanitize filename"""
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        # Check for path traversal
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, filename):
                raise ValueError("Filename contains invalid path characters")
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"|?*]', '', filename)
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:250] + ('.' + ext if ext else '')
        
        return sanitized
    
    @classmethod
    def validate_file_extension(cls, filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file extension"""
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in [ext.lower() for ext in allowed_extensions]
    
    @classmethod
    def validate_file_content(cls, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Validate file content using python-magic"""
        try:
            # Detect MIME type
            mime_type = magic.from_buffer(file_content, mime=True)
            
            # Get expected MIME type from filename
            expected_mime, _ = mimetypes.guess_type(filename)
            
            # Basic file type validation
            safe_mime_types = [
                'text/plain',
                'text/markdown',
                'application/pdf',
                'application/json',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/msword',
            ]
            
            if mime_type not in safe_mime_types:
                raise ValueError(f"File type {mime_type} is not allowed")
            
            # Check for file signature mismatches
            if expected_mime and expected_mime != mime_type:
                raise ValueError(f"File extension does not match content type")
            
            return {
                'mime_type': mime_type,
                'expected_mime': expected_mime,
                'size': len(file_content),
                'is_valid': True
            }
            
        except Exception as e:
            raise ValueError(f"File validation failed: {str(e)}")


class ChunkSearchRequest(BaseModel):
    """Validated chunk search request"""
    query: str = Field(..., min_length=2, max_length=500)
    limit: int = Field(10, ge=1, le=50)
    
    @validator('query')
    def validate_query(cls, v):
        return SecurityValidator.validate_text_input(v, "search query")


class ChunkListRequest(BaseModel):
    """Validated chunk list request"""
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
    search: Optional[str] = Field(None, max_length=500)
    source_file: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, pattern=r"^(help_data|stream_templates)$")
    sort_by: str = Field("creation_date", pattern=r"^(creation_date|filename|size)$")
    sort_order: str = Field("desc", pattern=r"^(asc|desc)$")
    
    @validator('search')
    def validate_search(cls, v):
        if v:
            return SecurityValidator.validate_text_input(v, "search query")
        return v
    
    @validator('source_file')
    def validate_source_file(cls, v):
        if v:
            return SecurityValidator.validate_filename(v)
        return v


class FileUploadValidator:
    """File upload validation"""
    
    def __init__(
        self,
        max_size: int = 50 * 1024 * 1024,  # 50MB
        allowed_extensions: List[str] = None
    ):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or [
            '.txt', '.md', '.pdf', '.docx', '.json'
        ]
    
    async def validate_upload(self, file: UploadFile) -> Dict[str, Any]:
        """Comprehensive file upload validation"""
        # Check filename
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        # Validate filename
        sanitized_filename = SecurityValidator.validate_filename(file.filename)
        
        # Check file extension
        if not SecurityValidator.validate_file_extension(sanitized_filename, self.allowed_extensions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension not allowed. Allowed extensions: {', '.join(self.allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Check file size
        if len(content) > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.max_size} bytes"
            )
        
        # Validate file content
        try:
            file_info = SecurityValidator.validate_file_content(content, sanitized_filename)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Check for empty files
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty files are not allowed"
            )
        
        # Generate file hash for deduplication
        file_hash = hashlib.sha256(content).hexdigest()
        
        return {
            'original_filename': file.filename,
            'sanitized_filename': sanitized_filename,
            'content': content,
            'size': len(content),
            'mime_type': file_info['mime_type'],
            'file_hash': file_hash,
            'validation_passed': True
        }


class RateLimitValidator:
    """Rate limiting validation"""
    
    @staticmethod
    def validate_rate_limit_config(config: str) -> tuple[int, int]:
        """Validate rate limit configuration string"""
        try:
            requests, period = config.split('/')
            requests = int(requests)
            
            period_mapping = {
                'second': 1,
                'minute': 60,
                'hour': 3600,
                'day': 86400
            }
            
            if period not in period_mapping:
                raise ValueError(f"Invalid period: {period}")
            
            if requests <= 0:
                raise ValueError("Request count must be positive")
            
            return requests, period_mapping[period]
            
        except ValueError as e:
            raise ValueError(f"Invalid rate limit format: {e}")


class DatabaseQueryValidator:
    """Database query validation"""
    
    @staticmethod
    def validate_sql_query(query: str) -> str:
        """Basic SQL query validation"""
        # Remove comments
        query = re.sub(r'--.*', '', query)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Check for dangerous operations
        dangerous_operations = [
            'drop', 'delete', 'truncate', 'alter', 'create',
            'insert', 'update', 'exec', 'execute', 'xp_',
            'sp_', 'grant', 'revoke'
        ]
        
        for operation in dangerous_operations:
            if re.search(rf'\b{operation}\b', query, re.IGNORECASE):
                raise ValueError(f"Operation '{operation}' is not allowed")
        
        return query
    
    @staticmethod
    def validate_limit_offset(limit: int, offset: int) -> tuple[int, int]:
        """Validate pagination parameters"""
        if limit < 1 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise ValueError("Offset must be non-negative")
        
        if offset > 100000:  # Prevent excessive offset attacks
            raise ValueError("Offset too large")
        
        return limit, offset


class APIKeyValidator:
    """API key validation (if authentication is implemented)"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            return False
        
        # API key should be alphanumeric and of specific length
        if not re.match(r'^[a-zA-Z0-9]{32,64}$', api_key):
            return False
        
        return True
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()


class ContentSecurityValidator:
    """Content security validation"""
    
    BLOCKED_DOMAINS = [
        'malware.com',
        'phishing.net',
        # Add more blocked domains
    ]
    
    SUSPICIOUS_PATTERNS = [
        r'password\s*[:=]\s*[^\s]+',
        r'api[_-]?key\s*[:=]\s*[^\s]+',
        r'secret\s*[:=]\s*[^\s]+',
        r'token\s*[:=]\s*[^\s]+',
        r'credential',
    ]
    
    @classmethod
    def scan_content_for_secrets(cls, content: str) -> List[str]:
        """Scan content for potential secrets"""
        findings = []
        
        for pattern in cls.SUSPICIOUS_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append(f"Potential secret detected: {match.group()[:20]}...")
        
        return findings
    
    @classmethod
    def validate_urls_in_content(cls, content: str) -> List[str]:
        """Validate URLs in content"""
        suspicious_urls = []
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, content, re.IGNORECASE)
        
        for url in urls:
            # Extract domain
            domain_match = re.search(r'(?:https?://)?(?:www\.)?([^/\s]+)', url)
            if domain_match:
                domain = domain_match.group(1).lower()
                if any(blocked in domain for blocked in cls.BLOCKED_DOMAINS):
                    suspicious_urls.append(url)
        
        return suspicious_urls


# Create validator instances
file_upload_validator = FileUploadValidator()
content_security_validator = ContentSecurityValidator()