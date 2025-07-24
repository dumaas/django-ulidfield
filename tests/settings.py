SECRET_KEY = "mock-key"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django_ulidfield",
    "tests",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True
