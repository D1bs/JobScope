from src.database import get_connection

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id            SERIAL PRIMARY KEY,
            hh_id         VARCHAR(50) UNIQUE,
            title         VARCHAR(200),
            company       VARCHAR(200),
            city          VARCHAR(100),
            salary_from   INTEGER,
            salary_to     INTEGER,
            url           TEXT,
            employment    VARCHAR(50),
            schedule      VARCHAR(50),
            contract_type VARCHAR(50),
            created_at    TIMESTAMP DEFAULT NOW()
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancy_skills (
            id              SERIAL PRIMARY KEY,
            vacancy_hh_id   VARCHAR(50),
            skill_name      VARCHAR(100),
            UNIQUE (vacancy_hh_id, skill_name)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("База данных инициализирована")

if __name__ == "__main__":
    init_db()