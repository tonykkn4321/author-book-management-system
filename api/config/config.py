import os

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Default to environment variable for flexibility
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    # Optional: add other shared config values here
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")


class ProductionConfig(Config):
    # Ensure the URI is set for production
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("Missing SQLALCHEMY_DATABASE_URI for production")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DEV_DATABASE_URI",
        "mysql+pymysql://root:Aa161616@localhost:3306/author_book_management_system"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URI", "sqlite:///:memory:")
