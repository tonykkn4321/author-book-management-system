import os

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Shared secret key
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}".format(
            user=os.getenv("PGUSER", "your_default_user"),
            password=os.getenv("PGPASSWORD", "your_default_password"),
            host=os.getenv("PGHOST", "localhost"),
            port=os.getenv("PGPORT", "5432"),
            dbname=os.getenv("PGDATABASE", "your_default_db")
        )
    )

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DEV_DATABASE_URI",
        "mysql+pymysql://root:Aa161616@localhost:3306/author_book_management_system"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URI",
        "sqlite:///:memory:"
    )
