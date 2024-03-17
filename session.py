from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

def init_session(url, base_class: DeclarativeBase):
    
    engine = create_engine(url)

    base_class.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()

