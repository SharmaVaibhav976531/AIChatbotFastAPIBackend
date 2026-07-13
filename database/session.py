from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.settings import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# 1. Create the SQLAlchemy Engine
# pool_pre_ping=True: Tests the connection for liveness before using it (prevents stale connection errors)
# pool_size & max_overflow: Configures the connection pool for production traffic
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,  # Set to True if you want to see raw SQL queries in the console
)

logger.info(f"Database engine created for: {settings.database_name}")

# 2. Create a SessionLocal class
# autocommit=False: We must explicitly commit transactions (Best Practice)
# autoflush=False: We must explicitly flush changes to the DB (Best Practice)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    FastAPI Dependency: Yields a database session.
    This ensures that every HTTP request gets its own isolated database session,
    and the session is properly closed when the request finishes.
    """
    db = SessionLocal()
    logger.info("Database session created.")
    try:
        yield db
        # If the route finishes without errors, FastAPI reaches here.
        # Note: We don't commit here. The Service layer will handle commits.
        logger.info("Database session yielded successfully.")
    except Exception:
        # If an error occurs in the route, we rollback to prevent partial data corruption
        logger.error("Database transaction failed. Rolling back.")
        db.rollback()
        raise
    finally:
        # This ALWAYS runs, ensuring no connection leaks
        db.close()
        logger.info("Database session closed.")