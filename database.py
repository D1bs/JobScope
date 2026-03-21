import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="jobscope",
        user="jobscope_user",
        password="1234"
    )
    return conn