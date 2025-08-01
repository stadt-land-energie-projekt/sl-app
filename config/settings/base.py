"""Base settings to build other settings files upon."""
from pathlib import Path

import environ
from django_mapengine import setup

ROOT_DIR = environ.Path(__file__) - 3  # (slapp/config/settings/base.py - 3 = slapp/)
APPS_DIR = ROOT_DIR.path("slapp")
DATA_DIR = APPS_DIR.path("data")
GEODATA_DIR = DATA_DIR.path("geodata")
ZIB_DATA = DATA_DIR.path("zib")
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# slapp/
APPS_DIR = BASE_DIR / "slapp"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/Berlin"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # Handy template tags
    "django.contrib.admin",
    "django_cotton",
    "django.forms",
    "django.contrib.gis",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_celery_beat",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "django_mapengine",
    "django_distill",
]

LOCAL_APPS = [
    "slapp.users",
    "slapp.explorer",
    "slapp.kommWertTool",
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "slapp.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "slapp.users.context_processors.allauth_settings",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Finn Hees""", "finn.hees@rl-institut.de")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = env.bool("DJANGO_ADMIN_FORCE_ALLAUTH", default=False)

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-extended
CELERY_RESULT_EXTENDED = True
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-backend-always-retry
# https://github.com/celery/celery/pull/6122
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-backend-max-retries
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-time-limit
CELERY_TASK_TIME_LIMIT = 5 * 60
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-soft-time-limit
CELERY_TASK_SOFT_TIME_LIMIT = 60
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#worker-send-task-events
CELERY_WORKER_SEND_TASK_EVENTS = True
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_send_sent_event
CELERY_TASK_SEND_SENT_EVENT = True
# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "email"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_USERNAME_REQUIRED = False
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = "slapp.users.adapters.AccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/forms.html
ACCOUNT_FORMS = {"signup": "slapp.users.forms.UserSignupForm"}
# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_ADAPTER = "slapp.users.adapters.SocialAccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/forms.html
SOCIALACCOUNT_FORMS = {"signup": "slapp.users.forms.UserSocialSignupForm"}
# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]

# django-libsass
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
COMPRESS_PRECOMPILERS = [("text/x-scss", "django_libsass.SassCompiler")]
COMPRESS_CACHEABLE_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"

# By Default swagger ui is available only to admin user(s). You can change permission classes to change that
# See more configuration options at https://drf-spectacular.readthedocs.io/en/latest/settings.html#settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Stadt-Land-Energie Webapp API",
    "DESCRIPTION": "Documentation of API endpoints of Stadt-Land-Energie Webapp",
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
}
# Your stuff...
# ------------------------------------------------------------------------------
# django-mapengine
# ------------------------------------------------------------------------------
# https://github.com/rl-institut/django-mapengine

MAP_ENGINE_CENTER_AT_STARTUP = [10.407237624103573, 51.22757621251938]
MAP_ENGINE_ZOOM_AT_STARTUP = 5.546712433728557
MAP_ENGINE_MAX_BOUNDS: [[-2.54, 46.35], [23.93, 55.87]]
MAP_ENGINE_LAYERS_AT_STARTUP = [
    "region",
    "regionline",
    "regionlabel",
    "municipality",
    "municipalityline",
    "municipalitylabel",
]

MAP_ENGINE_STYLES_FOLDER = "slapp/static/styles/"
MAP_ENGINE_MIN_ZOOM = 2

MAP_ENGINE_IMAGES = [
    setup.MapImage("wind", "images/icons/map_wind.png"),
    setup.MapImage("pv", "images/icons/map_pv.png"),
    setup.MapImage("hydro", "images/icons/map_hydro.png"),
    setup.MapImage("biomass", "images/icons/map_biomass.png"),
    setup.MapImage("combustion", "images/icons/map_combustion.png"),
    setup.MapImage("gsgk", "images/icons/map_gsgk.png"),
    setup.MapImage("storage", "images/icons/map_battery.png"),
    setup.MapImage("wind_plus", "images/icons/map_wind_plus.png"),
    setup.MapImage("pv_plus", "images/icons/map_pv_plus.png"),
    setup.MapImage("hydro_plus", "images/icons/map_hydro_plus.png"),
    setup.MapImage("biomass_plus", "images/icons/map_biomass_plus.png"),
    setup.MapImage("combustion_plus", "images/icons/map_combustion_plus.png"),
    setup.MapImage("gsgk_plus", "images/icons/map_gsgk_plus.png"),
    setup.MapImage("storage_plus", "images/icons/map_battery_plus.png"),
]

MAP_ENGINE_API_MVTS = {
    "region": [
        setup.MVTAPI("region", "explorer", "Region", style="region-fill", maxzoom=8),
        setup.MVTAPI("regionline", "explorer", "Region", style="region-line", maxzoom=8),
    ],
    "municipality": [
        setup.MVTAPI("municipality", "explorer", "Municipality", style="region-fill", minzoom=8),
        setup.MVTAPI("municipalityline", "explorer", "Municipality", style="region-line", minzoom=8),
        setup.MVTAPI("municipalitylabel", "explorer", "Municipality", "label_tiles", style="region-label", minzoom=8),
    ],
    "static": [
        setup.MVTAPI("landscape_protection_area", "explorer", "LandscapeProtectionArea"),
        setup.MVTAPI("forest", "explorer", "Forest"),
        setup.MVTAPI("special_protection_area", "explorer", "SpecialProtectionArea"),
        setup.MVTAPI("air_traffic", "explorer", "AirTraffic"),
        setup.MVTAPI("aviation", "explorer", "Aviation"),
        setup.MVTAPI("biosphere_reserve", "explorer", "BiosphereReserve"),
        setup.MVTAPI("drinking_water_protection_area", "explorer", "DrinkingWaterArea"),
        setup.MVTAPI("fauna_flora_habitat", "explorer", "FaunaFloraHabitat"),
        setup.MVTAPI("floodplain", "explorer", "Floodplain"),
        setup.MVTAPI("grid", "explorer", "Grid"),
        setup.MVTAPI("industry", "explorer", "Industry"),
        setup.MVTAPI("less_favoured_areas_agricultural", "explorer", "LessFavouredAreasAgricultural"),
        setup.MVTAPI("military", "explorer", "Military"),
        setup.MVTAPI("nature_conservation_area", "explorer", "NatureConservationArea"),
        setup.MVTAPI("railway", "explorer", "Railway"),
        setup.MVTAPI("road_default", "explorer", "Road"),
        setup.MVTAPI("waters", "explorer", "Water"),
        setup.MVTAPI("pv_ground_operating", "explorer", "RpgOlsPvGroundOperating"),
        setup.MVTAPI("pv_ground_planned", "explorer", "RpgOlsPvGroundPlanned"),
        setup.MVTAPI("potentialarea_wind_2018_eg", "explorer", "PotentialareaWindSTP2018EG"),
        setup.MVTAPI("potentialarea_wind_stp_2024_vr", "explorer", "PotentialareaWindSTP2024VR"),
        setup.MVTAPI("pv_ground_criteria_aviation", "explorer", "PvGroundCriteriaAviation"),
        setup.MVTAPI("pv_ground_criteria_biotopes", "explorer", "PvGroundCriteriaBiotopes"),
        setup.MVTAPI("pv_ground_criteria_forest", "explorer", "PvGroundCriteriaForest"),
        setup.MVTAPI("pv_ground_criteria_link_open_spaces", "explorer", "PvGroundCriteriaLinkedOpenSpaces"),
        setup.MVTAPI("pv_ground_criteria_merged", "explorer", "PvGroundCriteriaMerged"),
        setup.MVTAPI("pv_ground_criteria_moor", "explorer", "PvGroundCriteriaMoor"),
        setup.MVTAPI(
            "pv_ground_criteria_nature_conservation_area",
            "explorer",
            "PvGroundCriteriaNatureConservationArea",
        ),
        setup.MVTAPI("pv_ground_criteria_nature_monuments", "explorer", "PvGroundCriteriaNatureMonuments"),
        setup.MVTAPI("pv_ground_criteria_priority_areas", "explorer", "PvGroundCriteriaPriorityAreas"),
        setup.MVTAPI(
            "pv_ground_criteria_priority_areas_grassland",
            "explorer",
            "PvGroundCriteriaPriorityAreasGrassland",
        ),
        setup.MVTAPI(
            "pv_ground_criteria_priority_areas_permanent_crops",
            "explorer",
            "PvGroundCriteriaPriorityAreasPermanentCrops",
        ),
        setup.MVTAPI("pv_ground_criteria_settlements", "explorer", "PvGroundCriteriaSettlements"),
        setup.MVTAPI("pv_ground_criteria_settlements_200m", "explorer", "PvGroundCriteriaSettlements200m"),
        setup.MVTAPI("pv_ground_criteria_water_bodies", "explorer", "PvGroundCriteriaWaterBodies"),
    ],
}

MAP_ENGINE_API_CLUSTERS = [
    setup.ClusterAPI("wind", "explorer", "RpgOlsWindOperating", properties=["id"]),
    setup.ClusterAPI("wind_planned", "explorer", "RpgOlsWindPlanned", properties=["id"]),
    setup.ClusterAPI("pvroof", "explorer", "PVroof", properties=["id", "unit_count"]),
    setup.ClusterAPI("biomass", "explorer", "Biomass", properties=["id", "unit_count"]),
    setup.ClusterAPI("combustion", "explorer", "Combustion", properties=["id", "unit_count"]),
    setup.ClusterAPI("storage", "explorer", "Storage", properties=["id", "unit_count"]),
]

MAP_ENGINE_CHOROPLETHS = []
MAP_ENGINE_POPUPS = []
