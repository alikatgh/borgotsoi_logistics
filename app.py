import os
from flask import Flask, render_template, request, redirect
import sqlite3
from flask import flash
import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash # For password handling
from config import SECRET_KEY  # Import SECRET_KEY from config.py

app = Flask(__name__, static_folder='templates/static') 
app.config['SECRET_KEY'] = SECRET_KEY  # Replace with a secure key

# ... your database functions

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    def set_password(self, password):
        """Hashes the password for secure storage"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks a password against the stored hash"""
        return check_password_hash(self.password_hash, password)

    @classmethod  # Add a classmethod for loading from the database
    def get_by_username(cls, username):
        db_path = os.path.abspath('logistics.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username,)).fetchone()  
            if result:
                return cls(*result)  # Create a User object from the row
            return None

@login_manager.user_loader
def load_user(user_id):
    db_path = os.path.abspath('logistics.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        result = cursor.execute("""
            SELECT * FROM users WHERE user_id = ?
        """, (user_id,)).fetchone() 
        if result:
            return User(*result) 
        return None

def get_recent_orders():
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, supermarkets.name, order_date FROM orders JOIN supermarkets ON orders.supermarket_id = supermarkets.supermarket_id ORDER BY order_date DESC LIMIT 10")
        recent_orders = cursor.fetchall()
    return recent_orders

def add_order_to_database(order_data):
    db_path = os.path.abspath('logistics.db')

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (supermarket_id, items, order_date, delivery_date) VALUES (?, ?, ?, ?)",
                (order_data['supermarket_id'], order_data['items'], order_data['order_date'], order_data['delivery_date'])
            )
            conn.commit()  # Commit changes to the database
    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")  # Flash error message
        return False  # Indicate failure
    else:
        flash("Order placed successfully!", "success")
        return True  # Indicate success

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
        # Input Validation
        supermarket_id = request.form.get('supermarket_id')
        items = request.form.get('items')
        order_date_str = request.form.get('order_date')
        delivery_date_str = request.form.get('delivery_date')

        # Check for required fields
        if not all([supermarket_id, items, order_date_str]):
            flash("Please fill in all required fields.", "error")
            return redirect('/new_order')

        # Validate date formats
        try:
            order_date = datetime.datetime.strptime(order_date_str, '%Y-%m-%d').date()
            delivery_date = datetime.datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect('/new_order')

        # Additional validations you can add (e.g., supermarket_id exists, dates are in the future)

        # Process order submission
        order_data = {
            'supermarket_id': supermarket_id,
            'items': items,
            'order_date': order_date,
            'delivery_date': delivery_date
        }
        if not add_order_to_database(order_data):
            return redirect('/new_order')  # Redirect on failure
        else:
            return redirect('/')
    else:
        supermarkets = get_supermarkets()
        return render_template('order_form.html', supermarkets=supermarkets)

if __name__ == '__main__':
    app.run(debug=True) 
