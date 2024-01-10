from sqlalchemy import create_engine, pool, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging
import datetime
import os

load_dotenv(os.getcwd() + '/.env')

Base = declarative_base()

class Message(Base):
    __tablename__ = 'Message'
    id = Column(Integer, primary_key=True,autoincrement=True)
    chat_id = Column(String)
    model = Column(String)
    system = Column(String)
    prompt = Column(String)
    response = Column(String)
    temperature = Column(Float)
    max_token = Column(Integer)
    top_p = Column(Float)
    frequency = Column(Float)
    presence = Column(Float)
    time=Column(DateTime, default=datetime.datetime.now)

def init_db():

    user = os.getenv("USERNAME")

    SQLALCHEMY_DATABASE_URI = "mysql://{username}:{password}@{hostname}/{databasename}?charset=utf8mb4".format(
        username=user,
        password=os.getenv("MYSQL_API_KEY"),
        hostname= user + ".mysql.eu.pythonanywhere-services.com",
        databasename=user + "$aiti"
    )

    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URI, poolclass=pool.QueuePool, pool_size=10, max_overflow=20, pool_pre_ping=True)
    except SQLAlchemyError as e:
        logging.error(f"Failed to create engine: {str(e)}")
        return None

    return engine

def check_db_conn(engine):
    try:
        conn = engine.connect()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Failed to connect to database: {str(e)}")
        return False

def reconnect_db(engine):
    try:
        engine.dispose()
        engine.connect()
        return True
    except Exception as e:
        logging.error(f"Failed to reconnect to database: {str(e)}")
        return False

def start_session(engine):

    if not check_db_conn(engine):
           if not reconnect_db(engine):
               return False

    try:
        Session = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
        session = Session.begin()
    except SQLAlchemyError as e:
        logging.error(f"Failed to start session: {str(e)}")
        return False

    return session

