import os
from contextlib import contextmanager
 
from sqlalchemy import create_engine  
from sqlalchemy.orm import DeclarativeBase, sessionmaker  
 
 
class Base(DeclarativeBase):
    pass
 
 
def _build_engine():
    database_url = os.environ.get("DATABASE_URL", "sqlite:///simuladorcopa.db")
 
    connect_args = {}
    if database_url.startswith("sqlite:///") or database_url.startswith("sqlite+libsql://"):
        connect_args["check_same_thread"] = False
 
    return create_engine(
        database_url,
        connect_args=connect_args,
        echo=os.environ.get("SQL_DEBUG", "0") == "1",
    )
 
 
engine = _build_engine()
 
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
 
 
@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
 
 
def init_db():
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
 