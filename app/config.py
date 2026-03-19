from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_SSL_CA = os.getenv("DB_SSL_CA")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))

    CRYPT_PASSWORD = os.getenv("CRIPT_PASSWORD", "")

    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))

    RESET_PASSWORD_URL_BASE = os.getenv(
        "RESET_PASSWORD_URL_BASE",
        "http://localhost:3000/redefinir-senha",
    )

    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
