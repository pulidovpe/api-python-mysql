import os

class BaseConfig:
    """Configuración base para todos los entornos"""
    SECRET_KEY = os.getenv("APP_SECRET", "default_secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("APP_SECRET", "default_jwt_secret")


class DevelopmentConfig(BaseConfig):
    """Configuración para desarrollo"""
    DEBUG = True
    DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '3'))
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', '')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_DATABASE', 'api_python_mysql')}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"connect_timeout": DB_CONNECT_TIMEOUT},
        "pool_pre_ping": True,
    }


class ProductionConfig(BaseConfig):
    """Configuración para producción"""
    DEBUG = False
    DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '3'))
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', '')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_DATABASE', 'api_python_mysql')}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"connect_timeout": DB_CONNECT_TIMEOUT},
        "pool_pre_ping": True,
    }


class TestingConfig(BaseConfig):
    """Configuración para tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test_secret"  # 🔹 Clave fija para firmar/validar en tests


# Función auxiliar para elegir config según FLASK_ENV
def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig
