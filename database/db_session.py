from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from database.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from database.models import Book, GeneralBook, RareBook, AncientScript, User, Librarian, Scholar, Guest, Section, LendingRecord
    Base.metadata.create_all(bind=engine)

def shutdown_session(exception=None):
    db_session.remove()
