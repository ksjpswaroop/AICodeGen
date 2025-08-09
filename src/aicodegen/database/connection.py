"""Database connection and session management."""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base

# Database configuration from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aicodegen:aicodegen@localhost:5432/aicodegen"
)

# For testing, use SQLite in-memory database
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create engine based on environment
if os.getenv("TESTING"):
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """Database management utilities."""
    
    @staticmethod
    def create_tables() -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def drop_tables() -> None:
        """Drop all database tables."""
        Base.metadata.drop_all(bind=engine)
    
    @staticmethod
    def reset_database() -> None:
        """Reset database by dropping and recreating all tables."""
        DatabaseManager.drop_tables()
        DatabaseManager.create_tables()
    
    @staticmethod
    def get_session() -> Session:
        """Get a new database session."""
        return SessionLocal()
    
    @staticmethod
    def close_session(session: Session) -> None:
        """Close a database session."""
        session.close()


# Database health check
def check_database_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception:
        return False


# Database migration utilities
def get_database_url() -> str:
    """Get the current database URL."""
    return DATABASE_URL


def is_database_empty() -> bool:
    """
    Check if database is empty (no tables).
    
    Returns:
        True if database is empty, False otherwise
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return len(tables) == 0
    except Exception:
        return True
