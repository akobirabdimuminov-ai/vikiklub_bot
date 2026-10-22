import sqlite3

def init_db():
    conn = sqlite3.connect('bot_database.db', timeout=15)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            faculty TEXT,
            saturday_attend TEXT,
            has_laptop TEXT,
            phone_number TEXT,
            motivation TEXT,
            is_registered INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('bot_database.db', timeout=15)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
    conn.close()

def save_registration(user_id, full_name, faculty, saturday_attend, has_laptop, phone_number, motivation):
    conn = sqlite3.connect('bot_database.db', timeout=15)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET full_name = ?, faculty = ?, saturday_attend = ?, has_laptop = ?, phone_number = ?, motivation = ?, is_registered = 1 
        WHERE user_id = ?
    ''', (full_name, faculty, saturday_attend, has_laptop, phone_number, motivation, user_id))
    conn.commit()
    conn.close()

def is_user_registered(user_id):
    conn = sqlite3.connect('bot_database.db', timeout=15)
    cursor = conn.cursor()
    cursor.execute('SELECT is_registered FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1