from typing import Generator
from src.database import get_connection

def get_db() -> Generator:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()