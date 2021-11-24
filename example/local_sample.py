# Copy this file to local.py and fill the true values

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "example-instance-for-dev-use-only"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "sample_db_name",
        "USER": "sample_user",
        "PASSWORD": "sample_password",
        "HOST": "localhost",
        "PORT": "",
    }
}
