from database import get_connection

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id          SERIAL PRIMARY KEY,
            title       VARCHAR(200),
            company     VARCHAR(200),
            city        VARCHAR(100),
            salary_from INTEGER,
            salary_to   INTEGER,
            url         TEXT,
            created_at  TIMESTAMP DEFAULT NOW()
        );    
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print('База данных инициализирована')

if __name__ == '__main__':
    init_db()