"""
database/db.py
Database engine, session factory, and declarative Base.
Supports PostgreSQL / MySQL via DATABASE_URL (set in environment or .env).
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Examples:
#   PostgreSQL: postgresql://user:password@localhost:5432/content_studio
#   MySQL:      mysql+pymysql://user:password@localhost:3306/content_studio
DATABASE_URL = os.getenv("DATABASE_URL", " mysql+pymysql://root:Prasadmajji1234@localhost:3306/content_studio")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session, always closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
