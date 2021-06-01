from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Column,
)

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from sqlalchemy.ext.declarative import declarative_base

from decouple import config

DATABASE_URL = config("DATABASE_URL")


ENGINE = create_engine(DATABASE_URL, echo=False)
session_factory = sessionmaker(bind=ENGINE)
SESSION = scoped_session(session_factory)
BASE = declarative_base()


class QuoraData(BASE):
    __tablename__ = "quora_data"
    tg_id = Column(String(20), primary_key=True)
    tg_username = Column(String(100))
    quora_username = Column(String(100))
    answer_count = Column(Integer)

    def __init__(self, tg_id, tg_username, quora_username, answer_count):
        self.tg_id = tg_id
        self.tg_username = tg_username
        self.quora_username = quora_username
        self.answer_count = answer_count


BASE.metadata.create_all(ENGINE)


def does_exist(quora_username):
    return (
        SESSION.query(QuoraData)
        .filter(QuoraData.quora_username == quora_username)
        .first()
        is not None
    )


def add_account(quora_username, tg_id, tg_username, answer_count):
    account = QuoraData(tg_id, tg_username, quora_username, answer_count)
    SESSION.add(account)
    SESSION.commit()


def get_tg_id(quora_username):
    account = (
        SESSION.query(QuoraData)
        .filter(QuoraData.quora_username == quora_username)
        .first()
    )
    return account.tg_id
