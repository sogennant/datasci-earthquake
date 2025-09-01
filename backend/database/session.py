import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.api.config import settings

logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

# Global engine instance to reuse across function invocations
_engine = None
_SessionLocal = None


def _get_database_url() -> str:
    match settings.environment:
        case "local":
            return settings.localhost_database_url_sqlalchemy
        case "ci" | "prod":
            return settings.neon_url
        case "dev_docker":
            return settings.database_url_sqlalchemy
        case _:
            raise ValueError(f"Unknown environment: {settings.environment}")


def get_engine():
    """Get or create database engine with connection pooling"""
    global _engine
    if _engine is None:
        _engine = create_engine(
            _get_database_url(),
            pool_size=20,
            pool_timeout=30,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_reset_on_return="commit",
            echo=False,  # Disable SQL logging in production
        )
    return _engine


def get_session_factory():
    """Get or create session factory"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


# Dependency function to get a database session
def get_db():
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


# Function to warm up the connection pool
def warm_up_connection_pool():
    """Warm up the database connection pool to reduce cold start latency"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logging.info("Database connection pool warmed up successfully")
    except Exception as e:
        logging.warning(f"Failed to warm up connection pool: {e}")
