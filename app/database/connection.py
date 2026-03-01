"""
database/connection.py
"""

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base

load_dotenv()


def get_database_url() -> str:
    host     = os.getenv("DB_HOST", "localhost")
    port     = os.getenv("DB_PORT", "5432")
    name     = os.getenv("DB_NAME", "ai_news")
    user     = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")

    # quote_plus encodes special characters like @ % # in password
    password_encoded = quote_plus(password)

    return f"postgresql+psycopg2://{user}:{password_encoded}@{host}:{port}/{name}"


# Module-level engine & factory
engine         = create_engine(get_database_url(), echo=False)
SessionFactory = sessionmaker(bind=engine)


def init_db() -> None:
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(engine)
    print("✅ Database tables created / verified.")


def get_session() -> Session:
    """Return a new database session. Caller must close it."""
    return SessionFactory()