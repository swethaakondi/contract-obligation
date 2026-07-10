import sqlite3

def create_database():
    conn = sqlite3.connect('database/contracts.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_name TEXT,
        upload_date TEXT,
        contract_text TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS obligations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        obligation_type TEXT,
        due_date TEXT,
        responsible_person TEXT,
        clause_text TEXT,
        risk_level TEXT,
        summary TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        obligation_id INTEGER,
        reminder_date TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("Database Created Successfully!")

create_database()