import base64
import hashlib
import secrets


def generate_code_verifier() -> str:
    verifier = secrets.token_urlsafe(64)
    return verifier[:128]


def generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def generate_state() -> str:
    return secrets.token_urlsafe(32)
