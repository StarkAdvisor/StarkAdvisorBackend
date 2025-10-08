from pymongo import MongoClient
from django.conf import settings


def get_mongo_client():
    """Return a pymongo database instance.

    This function is defensive: if `MONGO_DB` is not present in Django settings
    it raises a clear RuntimeError explaining how to fix the environment
    (usually by pointing `DJANGO_SETTINGS_MODULE` to a settings module that
    defines `MONGO_DB`, e.g. `starkadvisorbackend.settings.local`).
    """
    mongo_cfg = getattr(settings, "MONGO_DB", None)
    if not mongo_cfg:
        raise RuntimeError(
            "MONGO_DB is not configured in Django settings. "
            "Set DJANGO_SETTINGS_MODULE to a settings module that defines MONGO_DB "
            "(for example 'starkadvisorbackend.settings.local') or add MONGO_DB to your .env/.settings."
        )

    # Prefer full URI when present
    uri = mongo_cfg.get("URI") if isinstance(mongo_cfg, dict) else None
    if uri:
        client = MongoClient(uri)
    else:
        host = mongo_cfg.get("HOST") if isinstance(mongo_cfg, dict) else None
        port = mongo_cfg.get("PORT") if isinstance(mongo_cfg, dict) else None
        client = MongoClient(host or "localhost", port or 27017)

    db_name = mongo_cfg.get("NAME") if isinstance(mongo_cfg, dict) else None
    return client[db_name or "starkadvisor"]