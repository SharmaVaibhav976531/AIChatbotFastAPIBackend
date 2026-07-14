# database/base.py

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Using SQLAlchemy 2.0 DeclarativeBase style.
    All models (User, Session, Message) will inherit from this class.
    """
    pass