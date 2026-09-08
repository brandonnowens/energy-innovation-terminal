"""Cryptographic and security utilities for authentication and token management.

Uses Python standard library (hashlib, hmac, secrets, base64) to ensure 
maximum security (NIST-standard PBKDF2-SHA256 with 600k iterations and RFC 7519 HMAC-SHA256 JWT)
with zero binary/DLL dependency issues across all deployment environments.
"""

import base64
import json
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Any, Dict

from app.config import settings


def _b64url_encode(data: bytes) -> str:
    """Encode bytes to Base64URL string without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    """Decode Base64URL string with proper padding."""
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with 600,000 iterations and 16-byte random salt.
    Format: pbkdf2_sha256$iterations$salt_b64$hash_b64
    """
    if not password:
        raise ValueError("Password cannot be empty")
    salt = secrets.token_bytes(16)
    iterations = 600_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(derived).decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash in constant time."""
    if not plain_password or not hashed_password:
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2].encode("ascii"))
        expected_hash = base64.b64decode(parts[3].encode("ascii"))
        derived = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(derived, expected_hash)
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed RFC 7519 HMAC-SHA256 JWT access token."""
    header = {"alg": "HS256", "typ": "JWT"}
    to_encode = data.copy()
    now = datetime.utcnow()
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "iss": "nyserda-innovation-hub"
    })
    
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(to_encode, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and cryptographically verify a JWT access token."""
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_sig = hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
            
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            return None
            
        return payload
    except Exception:
        return None


def generate_random_token(length: int = 32) -> str:
    """Generate a high-entropy URL-safe random token."""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Compute SHA-256 hash of a token for secure database indexing."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
