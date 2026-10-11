import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

SQLALCHEMY_DB_URL = URL.create(
    "mssql+pyodbc",
    username=DB_USER,
    password=DB_PASSWORD,   # URL.create safely handles special characters like @ ! #
    host=DB_SERVER,
    database=DB_NAME,
    query={
        "driver": DB_DRIVER,
        "TrustServerCertificate": "yes",
    },
)

engine = create_engine(
    SQLALCHEMY_DB_URL,
    pool_pre_ping=True,
    fast_executemany=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

