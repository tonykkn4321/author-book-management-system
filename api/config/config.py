import os

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "your-default-salt")

    # Mail settings
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "your_email_address")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your_email_address")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your_email_password")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True") == "True"

    # ✅ Upload folder configuration
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DEV_DATABASE_URI",
        "mysql+pymysql://root:Aa161616@localhost:3306/author_book_management_system"
    )

class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Use in-memory SQLite for fast, isolated tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Security keys for testing
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret'
    SECURITY_PASSWORD_SALT = 'test-password-salt'

    # Disable CSRF protection for testing forms
    WTF_CSRF_ENABLED = False

    # Propagate exceptions to help with debugging
    PROPAGATE_EXCEPTIONS = True

    # Mail settings
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "your_email_address")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your_email_address")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your_email_password")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True") == "True"

    # Upload folder (can be mocked or redirected)
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'test_uploads')




