from typing import Generator
from database import get_connection

def get_db() -> Generator:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()