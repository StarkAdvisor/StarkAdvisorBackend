"""Helper to initialize Django in scripts reliably.

Usage:
    from starkadvisorbackend.utils.django_setup import ensure_django
    ensure_django()

The helper will:
- Respect an existing DJANGO_SETTINGS_MODULE if it points to a concrete settings module.
- If DJANGO_SETTINGS_MODULE is unset or points to the package 'starkadvisorbackend.settings', it will fall back to
  'starkadvisorbackend.settings.local' (development-friendly).
- Call django.setup() exactly once and return the loaded settings object for convenience.
- Optionally validate that required apps are present.
"""
from __future__ import annotations

import os
import importlib
from typing import Optional


def ensure_django(require_apps: Optional[list[str]] = None):
    """Ensure Django is configured and initialized.

    Args:
        require_apps: optional list of app names that must be present in INSTALLED_APPS; if any missing, raises RuntimeError.

    Returns:
        django.conf.settings (the loaded settings object)
    """
    current = os.environ.get("DJANGO_SETTINGS_MODULE")
    if not current or current.strip() == "starkadvisorbackend.settings":
        # fallback to local for convenience in development; production should set DJANGO_SETTINGS_MODULE explicitly
        os.environ["DJANGO_SETTINGS_MODULE"] = "starkadvisorbackend.settings.local"

    # Import and setup Django
    import django
    django.setup()

    from django.conf import settings as dj_settings

    if require_apps:
        missing = [a for a in require_apps if a not in getattr(dj_settings, "INSTALLED_APPS", [])]
        if missing:
            raise RuntimeError(
                f"Missing required apps in INSTALLED_APPS: {missing}. \n"
                f"Current DJANGO_SETTINGS_MODULE={os.environ.get('DJANGO_SETTINGS_MODULE')}"
            )

    return dj_settings
