"""
models/user.py
Users table — stores account credentials.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # stored as a bcrypt hash
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    contents = relationship(
        "GeneratedContent", back_populates="user", cascade="all, delete-orphan"
    )
