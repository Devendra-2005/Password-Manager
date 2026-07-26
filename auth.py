import hashlib
import os
import secrets

def generate_salt() -> str:
    """
    Generates a secure 16-byte random salt returned as a hex string.
    """
    return secrets.token_hex(16)

def hash_password(password: str, salt: str) -> str:
    """
    Hashes a password with a salt using PBKDF2 HMAC SHA-256 with 100,000 iterations.
    Returns the hex-encoded digest string.
    """
    salt_bytes = salt.encode('utf-8')
    password_bytes = password.encode('utf-8')
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password_bytes,
        salt_bytes,
        iterations=100000
    )
    return key.hex()

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """
    Verifies an input password against the stored hash and salt.
    """
    computed_hash = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, stored_hash)

def evaluate_password_strength(password: str) -> tuple[int, str, str]:
    """
    Evaluates password strength.
    Returns (score 0-100, label string, color hex).
    """
    if not password:
        return 0, "Empty", "#EF4444"

    score = 0
    length = len(password)

    # Length criteria
    if length >= 8:
        score += 20
    if length >= 12:
        score += 20
    if length >= 16:
        score += 10

    # Character composition
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    types_count = sum([has_lower, has_upper, has_digit, has_special])
    score += types_count * 12.5

    score = min(100, int(score))

    if score < 40:
        return score, "Weak", "#EF4444"
    elif score < 75:
        return score, "Medium", "#F59E0B"
    elif score < 90:
        return score, "Strong", "#10B981"
    else:
        return score, "Very Strong", "#059669"
