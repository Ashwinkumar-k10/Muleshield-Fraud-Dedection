import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///muleshield_local.db")

# Create engine and sessionmaker
# For SQLite, check if we need to set check_same_thread=False
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency helper to yield database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initializes the database schema by creating all registered tables.
    """
    import backend.database.models # Import models to register metadata
    Base.metadata.create_all(bind=engine)
    print("Database schema verified and initialized.")
