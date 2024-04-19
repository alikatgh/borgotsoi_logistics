import os
import sqlite3

DB_FILENAME = 'logistics.db'

def get_db_connection():
    db_path = os.path.abspath(DB_FILENAME)
    return sqlite3.connect(db_path)

def create_orders_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            supermarket_id INTEGER, 
            order_date DATETIME,
            order_status TEXT,
            delivery_date DATETIME,
            FOREIGN KEY(supermarket_id) REFERENCES supermarkets(supermarket_id) 
        )
    """)
    conn.commit()  # Commit changes

def create_supermarkets_table():
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supermarkets (
                supermarket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        """)

def create_users_table():
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT 
            )
        """)


if __name__ == '__main__':
    create_orders_table()
    create_supermarkets_table()
    create_users_table()
