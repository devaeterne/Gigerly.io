# api/app/utils/validators.py
"""Custom validation functions"""

import re
import mimetypes
from typing import List, Optional, Tuple
from urllib.parse import urlparse
import magic  # python-magic for file type detection

def validate_email_format(email: str) -> bool:
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone: str, country_code: Optional[str] = None) -> bool:
    """Basic phone number validation"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Basic length check (7-15 digits for international numbers)
    if len(digits) < 7 or len(digits) > 15:
        return False
    
    # If country code specified, do more specific validation
    if country_code == "US":
        return len(digits) == 10 or (len(digits) == 11 and digits[0] == '1')
    elif country_code == "TR":
        return len(digits) == 10 and digits.startswith('5')
    
    return True

def validate_url(url: str, require_https: bool = False) -> bool:
    """Validate URL format"""
    try:
        parsed = urlparse(url)
        
        # Check if scheme is present
        if not parsed.scheme:
            return False
        
        # Check if netloc (domain) is present
        if not parsed.netloc:
            return False
        
        # Check HTTPS requirement
        if require_https and parsed.scheme != 'https':
            return False
        
        # Check if scheme is http or https
        if parsed.scheme not in ['http', 'https']:
            return False
        
        return True
    except Exception:
        return False

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file extension is allowed"""
    if not filename:
        return False
    
    # Get file extension
    _, ext = filename.rsplit('.', 1) if '.' in filename else ('', '')
    ext = ext.lower()
    
    # Check against allowed extensions
    return ext in [e.lower() for e in allowed_extensions]

def validate_file_type(file_content: bytes, allowed_types: List[str]) -> bool:
    """Validate file type using magic numbers (more secure than extension check)"""
    try:
        # Detect MIME type from file content
        mime_type = magic.from_buffer(file_content, mime=True)
        return mime_type in allowed_types
    except Exception:
        return False

def validate_image_dimensions(
    width: int, 
    height: int, 
    max_width: int = 4096, 
    max_height: int = 4096,
    min_width: int = 32,
    min_height: int = 32
) -> bool:
    """Validate image dimensions"""
    return (min_width <= width <= max_width and 
            min_height <= height <= max_height)

def validate_file_size(size: int, max_size_mb: int = 10) -> bool:
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return 0 < size <= max_size_bytes

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Validate password strength and return issues"""
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")
    
    # Check for common weak passwords
    weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
    if password.lower() in weak_passwords:
        issues.append("Password is too common")
    
    return len(issues) == 0, issues

def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """Validate username format"""
    # Username rules: 3-30 chars, alphanumeric + underscore/hyphen, no spaces
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return False, "Username must be no more than 30 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    # Can't start or end with underscore/hyphen
    if username.startswith(('_', '-')) or username.endswith(('_', '-')):
        return False, "Username cannot start or end with underscore or hyphen"
    
    # Reserved usernames
    reserved = ['admin', 'api', 'www', 'mail', 'ftp', 'support', 'help', 'root']
    if username.lower() in reserved:
        return False, "Username is reserved"
    
    return True, None

def validate_slug(slug: str) -> bool:
    """Validate URL slug format"""
    # Slug rules: lowercase, alphanumeric + hyphens, no consecutive hyphens
    if not slug:
        return False
    
    if not re.match(r'^[a-z0-9-]+$', slug):
        return False
    
    if '--' in slug:  # No consecutive hyphens
        return False
    
    if slug.startswith('-') or slug.endswith('-'):
        return False
    
    return True