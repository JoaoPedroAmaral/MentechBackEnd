from __future__ import annotations

import os
from typing import Optional

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

from app.config import Config

_pool: Optional[MySQLConnectionPool] = None


def _resolve_ssl_ca() -> Optional[str]:
    if not Config.DB_SSL_CA:
        return None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(base_dir, Config.DB_SSL_CA.replace("backend/", ""))
    return candidate if os.path.exists(candidate) else None


def get_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is not None:
        return _pool

    ssl_ca = _resolve_ssl_ca()
    pool_args = {
        "pool_name": "mentech_pool",
        "pool_size": Config.DB_POOL_SIZE,
        "host": Config.DB_HOST,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "database": Config.DB_NAME,
        "port": Config.DB_PORT,
    }
    if ssl_ca:
        pool_args["ssl_ca"] = ssl_ca
        pool_args["ssl_verify_cert"] = True

    _pool = MySQLConnectionPool(**pool_args)
    return _pool


def get_connection() -> mysql.connector.connection.MySQLConnection:
    return get_pool().get_connection()
