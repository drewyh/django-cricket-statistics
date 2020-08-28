#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent


def main():
    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
        from django.conf import settings
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # configure the settings as a standalone app
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(BASE_DIR / "db.sqlite3"),
            }
        },
        SECRET_KEY="placeholder-key",
        INSTALLED_APPS=["django_cricket_statistics", "tests"],
        PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
    )

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
