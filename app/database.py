# app/database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Resolve absolute paths relative to this file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure the folder exists
os.makedirs(DATA_DIR, exist_ok=True)

BIBLE_DB_PATH = os.path.join(DATA_DIR, "bible.db")
ARCHIVE_DB_PATH = os.path.join(DATA_DIR, "devotionals.db")

# Engines
BIBLE_ENGINE = create_engine(f"sqlite:///{BIBLE_DB_PATH}", connect_args={"check_same_thread": False})
ARCHIVE_ENGINE = create_engine(f"sqlite:///{ARCHIVE_DB_PATH}", connect_args={"check_same_thread": False})

Base = declarative_base()

class Devotional(Base):
    __tablename__ = "devotionals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    scripture_ref = Column(String(100))
    scripture_text = Column(Text)
    reflection = Column(Text)
    application = Column(Text)
    prayer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Session factory for archive DB
ArchiveSessionLocal = sessionmaker(bind=ARCHIVE_ENGINE, autoflush=False, autocommit=False)

# Ensure archive tables exist
Base.metadata.create_all(bind=ARCHIVE_ENGINE)
