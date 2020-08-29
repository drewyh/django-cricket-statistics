# settings for tests and migrations
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent


DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
}

SECRET_KEY = "placeholder-key"
INSTALLED_APPS = ["django_cricket_statistics", "tests"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
