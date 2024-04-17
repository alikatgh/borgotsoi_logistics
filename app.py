import os
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def create_orders_table():
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supermarket_id INTEGER, 
                order_date DATETIME,
                order_status TEXT,
                delivery_date DATETIME,
                FOREIGN KEY(supermarket_id) REFERENCES supermarkets(supermarket_id) 
            )
        """)

def create_supermarkets_table():
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE supermarkets (
                supermarket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        """)

def get_recent_orders():
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, supermarkets.name, order_date FROM orders JOIN supermarkets ON orders.supermarket_id = supermarkets.supermarket_id ORDER BY order_date DESC LIMIT 10")
        recent_orders = cursor.fetchall()
    return recent_orders

def add_order_to_database(order_data):
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (supermarket_id, items, order_date) VALUES (?, ?, ?)",
            (order_data['supermarket_id'], order_data['items'], order_data['order_date'])
        )

def get_supermarkets():
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT supermarket_id, name FROM supermarkets")  # Use supermarket_id here
        supermarkets = cursor.fetchall()
    return supermarkets

@app.route('/')
def index():
    orders = get_recent_orders()
    return render_template('index.html', orders=orders)

@app.route('/new_order', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        add_order_to_database(request.form)
        return redirect('/')
    else:
        supermarkets = get_supermarkets()
        return render_template('order_form.html', supermarkets=supermarkets)

if __name__ == '__main__':
    # Optionally call table creation functions here
    create_orders_table()
    create_supermarkets_table()  

    app.run(debug=True) 
