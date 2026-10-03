from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ ОБЯЗАТЕЛЬНО поменяй на свой секретный ключ!
SECRET_KEY = "django-insecure-change-me-to-random-string-please"

DEBUG = True  # На PythonAnywhere должно быть False!

ALLOWED_HOSTS = ["*"]  # На PythonAnywhere лучше указать ваш_логин.pythonanywhere.com

# ============ НАСТРОЙКИ САЙТА ============

# Пароль для входа в админку
ADMIN_PASSWORD = "admin123"  # ⚠️ поменяй!

# За сколько часов до начала предмета открывается запись
HOURS_BEFORE_OPEN = 24

# Название сайта
SITE_NAME = "Запись на лабы"

# ============ ПРИЛОЖЕНИЯ ============

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bookings",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lab_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "bookings.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "lab_site.wsgi.application"

# ============ БАЗА ДАННЫХ ============

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ============ АУТЕНТИФИКАЦИЯ ============

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/subjects/"
LOGOUT_REDIRECT_URL = "/"

# ============ ЛОКАЛИЗАЦИЯ ============

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# ============ СТАТИКА ============

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"