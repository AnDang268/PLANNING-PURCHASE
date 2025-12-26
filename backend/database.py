
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import urllib.parse
import os
from dotenv import load_dotenv, set_key

# Load environment variables
load_dotenv(override=True)

# Global variables for Engine and SessionLocal
engine = None
SessionLocal = None
Base = declarative_base()

def get_connection_string():
    server = os.getenv("DB_SERVER", "localhost")
    database = os.getenv("DB_DATABASE", "PlanningPurchaseDB")
    username = os.getenv("DB_USER", "sa")
    password = os.getenv("DB_PASSWORD", "sqlP@ssw0rd")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    # Construct connection string
    # Try appending UTF-8 charset explicitly just in case, though ODBC 17 handles it.
    params = urllib.parse.quote_plus(
        f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    )
    return f"mssql+pyodbc:///?odbc_connect={params}"

from sqlalchemy import event
import pyodbc

def init_db():
    global engine, SessionLocal
    url = get_connection_string()
    
    engine = create_engine(
        url, 
        fast_executemany=False,
    )
    
    # --- UNICODE FIX: FORCE PYODBC ENCODING ---
    # --- UNICODE FIX: FORCE PYODBC ENCODING ---
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_connection, connection_record):
        # Force UTF-8 for parsing char/varchar/text
        # dbapi_connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
        # dbapi_connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8') # CAUSES CRASH ON READ
        # dbapi_connection.setencoding(encoding='utf-8')
        pass
    # ------------------------------------------
    # ------------------------------------------

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"DATABASE INITIALIZED: {os.getenv('DB_SERVER')}/{os.getenv('DB_DATABASE')}")

# Initialize on module load
init_db()

def get_db():
    global SessionLocal
    if SessionLocal is None:
        init_db()
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def reload_engine():
    """Reloads the database engine with fresh environment variables."""
    # Force reload .env
    load_dotenv(override=True)
    init_db()

# Expose current config for UI display
server = os.getenv("DB_SERVER", "localhost")
database = os.getenv("DB_DATABASE", "PlanningPurchaseDB")
username = os.getenv("DB_USER", "sa")
