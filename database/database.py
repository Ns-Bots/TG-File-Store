from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import os
import threading
import asyncio

from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, UniqueConstraint, func

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def start() -> scoped_session:
    engine = create_engine(DATABASE_URL, client_encoding="utf8")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))

BASE = declarative_base()
SESSION = start()

INSERTION_LOCK = threading.RLock()

class Database(BASE):
    __tablename__ = "database"
    id = Column(String, primary_key=True)
    up_name = Column(Boolean)

    def __init__(self, id, up_name):
        self.id = str(id)
        self.up_name = up_name

Database.__table__.create(checkfirst=True)

async def update_as_name(id, mode):
    with INSERTION_LOCK:
        msg = SESSION.query(Database).get(str(id))
        if not msg:
            msg = Database(str(id), False)
        else:
            msg.up_name = mode
            SESSION.delete(msg)
        SESSION.add(msg)
        SESSION.commit()

async def get_data(id):
    try:
        user_data = SESSION.query(Database).get(str(id))
        if not user_data:
            new_user = Database(str(id), False)
            SESSION.add(new_user)
            SESSION.commit()
            user_data = SESSION.query(Database).get(str(id))
        return user_data
    finally:
        SESSION.close()


