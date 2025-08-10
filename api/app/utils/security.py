# api/app/utils/security.py
"""Security utility functions"""

import secrets
import string
import hashlib
import re
from typing import Optional
import base64
import os

def generate_random_string(length: int = 32) -> str:
    """Generate a cryptographically secure random string"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secure_token(length: int = 64) -> str:
    """Generate a secure token for API keys, reset tokens, etc."""
    return secrets.token_urlsafe(length)

def hash_file(file_content: bytes) -> str:
    """Generate SHA-256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal attacks"""
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def is_safe_url(url: str, allowed_hosts: list = None) -> bool:
    """Check if URL is safe for redirects"""
    if not url:
        return False
    
    # Check for absolute URLs
    if url.startswith(('http://', 'https://')):
        if allowed_hosts:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.hostname in allowed_hosts
        return False
    
    # Relative URLs are generally safe
    return url.startswith('/')

def mask_email(email: str) -> str:
    """Mask email for privacy (e.g., for logs)"""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"

def generate_api_key() -> str:
    """Generate API key in standard format"""
    prefix = "fp_"  # Freelancer Platform
    key = generate_secure_token(32)
    return f"{prefix}{key}"

def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks"""
    return secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8'))