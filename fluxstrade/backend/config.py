import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.getenv("SESSION_FILE_DIR", "./.flask_session")
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]

    DERIV_CLIENT_ID = os.getenv("DERIV_CLIENT_ID", "")
    DERIV_APP_ID = os.getenv("DERIV_APP_ID") or DERIV_CLIENT_ID
    DERIV_REDIRECT_URI = os.getenv("DERIV_REDIRECT_URI", "http://localhost:5000/api/callback")
    DERIV_AUTH_URL = os.getenv("DERIV_AUTH_URL", "https://auth.deriv.com/oauth2/auth")
    DERIV_TOKEN_URL = os.getenv("DERIV_TOKEN_URL", "https://auth.deriv.com/oauth2/token")
    DERIV_API_BASE_URL = os.getenv("DERIV_API_BASE_URL", "https://api.derivws.com").rstrip("/")
    DERIV_OAUTH_SCOPE = os.getenv("DERIV_OAUTH_SCOPE", "trade account_manage")
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "15"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
