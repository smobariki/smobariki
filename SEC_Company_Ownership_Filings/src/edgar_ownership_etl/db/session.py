from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from edgar_ownership_etl.config import settings

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False)
