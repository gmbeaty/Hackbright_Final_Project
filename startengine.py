from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from SQL_Alchemy_LXML import Base

def create_session(engine=None):
    engine = engine or create_engine("sqlite:///rss.db", echo=True)
    session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))
    Base.query = session.query_property()

    return session
