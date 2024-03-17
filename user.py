from os import urandom
import json
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.sql import func
from hashlib import pbkdf2_hmac

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

url = None
with open('config.json') as f:
    json_config = json.load(f)
    url = json_config['user_url'] if json_config is not None else "sqlite:///user.db"

engine = create_engine(url)

class UserBase(DeclarativeBase):
    pass

class User(UserBase):
    __tablename__ = "user_table"

    user: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str]
    user_space: Mapped[str]

    time_created = mapped_column(DateTime(timezone=True), server_default=func.now())

class Salt(UserBase):
    __tablename__ = "salt_table"
    
    user: Mapped[str] = mapped_column(ForeignKey(User.user), primary_key=True)
    salt: Mapped[str]
    hash: Mapped[str]    

iters_ = 500_000
UserBase.metadata.create_all(engine)

def user_create(user: str, password: str, hash_func:str) -> bool:
    
    with Session(engine) as session:

        salt = urandom(32)
        salt_ = Salt(user=user, salt=salt)

        hashed_password = pbkdf2_hmac(hash_func, password.encode('utf-8'), salt, iters_)
        user_ = User(user = user, password = hashed_password, hash = hash_func)

        session.add(user_)
        session.add(salt_)
        try:
            session.commit()
        except:
            session.rollback()
            return False
        
        return True

def user_has(user: str) -> bool:
    
    with Session(engine) as session:
        return session.query(User).filter(User.user == user).count() > 0

def user_validate(user: str, password: str) -> bool:
    
    with Session(engine) as session:
        pass
    
def user_change_password(user: str, password: str, new_password: str, new_hash: str | None) -> bool:
    
    with Session(engine) as session:
        pass

def user_delete(user: str, password: str) -> bool:
    
    with Session(engine) as session:
        pass