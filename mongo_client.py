import os
from urllib.parse import urlparse
from typing import Optional
from pymongo import MongoClient
from django.conf import settings

_CLIENT: Optional[MongoClient] = None

def get_mongo_client():
    """Return a pymongo Database instance (reusable connection).
    Prioriza Azure env (MONGODB_URI/MONGO_DB) y usa settings.MONGO_DB como fallback.
    Valida con ping e incluye TLS para Atlas (mongodb+srv).
    """
    global _CLIENT

    # 1) Azure env
    env_uri = os.getenv("MONGODB_URI")
    env_db  = os.getenv("MONGO_DB") or "starkadvisor"

    # 2) Fallback a settings.MONGO_DB
    mongo_cfg = getattr(settings, "MONGO_DB", None)

    if env_uri:
        uri = env_uri
        db_name = env_db
    else:
        if not mongo_cfg:
            raise RuntimeError(
                "No Mongo config found. Define MONGODB_URI/MONGO_DB en Azure App Settings "
                "o settings.MONGO_DB (dict con URI/HOST/PORT/NAME)."
            )
        uri = mongo_cfg.get("URI") if isinstance(mongo_cfg, dict) else None
        if not uri:
            host = mongo_cfg.get("HOST") if isinstance(mongo_cfg, dict) else None
            port = mongo_cfg.get("PORT") if isinstance(mongo_cfg, dict) else None
            name = mongo_cfg.get("NAME") if isinstance(mongo_cfg, dict) else "starkadvisor"
            uri = f"mongodb://{host or 'localhost'}:{port or 27017}/{name}"
            db_name = name
        else:
            db_name = mongo_cfg.get("NAME") if isinstance(mongo_cfg, dict) else "starkadvisor"

    def _needs_tls(u: str) -> bool:
        if u.startswith("mongodb+srv://"):
            return True
        try:
            host = urlparse(u.replace("mongodb://", "http://", 1)).hostname or ""
        except Exception:
            host = ""
        return host.endswith(".mongodb.net")

    if _CLIENT is None:
        _CLIENT = MongoClient(
            uri,
            tls=_needs_tls(uri),
            serverSelectionTimeoutMS=4000,
            connectTimeoutMS=4000,
            socketTimeoutMS=8000,
        )
        _CLIENT.admin.command("ping")  # valida 1 vez

    return _CLIENT[db_name]
