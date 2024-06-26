import os
from flask import Flask, render_template, request, redirect
import sqlite3
from flask import flash
import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash # For password handling
from config import SECRET_KEY  # Import SECRET_KEY from config.py
from flask import jsonify  # Import for creating JSON responses

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
    print('Database path:', db_path)  # Check the path

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # in case you want get back to order date
        # query = "SELECT order_id, supermarkets.name, order_date FROM orders JOIN supermarkets ON orders.supermarket_id = supermarkets.supermarket_id ORDER BY order_date DESC LIMIT 10"
        # unless, use this
        query = "SELECT order_id, supermarkets.name, delivery_date FROM orders JOIN supermarkets ON orders.supermarket_id = supermarkets.supermarket_id ORDER BY order_date DESC LIMIT 10"
        print('Executing query:', query)  # Show the query
        cursor.execute(query)
        recent_orders = cursor.fetchall()
        print('Orders fetched:', recent_orders)  # Did you get results?
    return recent_orders


def add_order_to_database(order_data):
    db_path = os.path.abspath('logistics.db')  # Ensure correct path

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Validate supermarket_id (if desired)
            cursor.execute("SELECT COUNT(*) FROM supermarkets WHERE supermarket_id = ?", (order_data['supermarket_id'],))
            if cursor.fetchone()[0] == 0:
                flash('Invalid supermarket ID', 'error')
                return False

            cursor.execute(
                "INSERT INTO orders (supermarket_id, items, delivery_date, delivery_status) VALUES (?, ?, ?, ?)",
                (order_data['supermarket_id'], order_data['items'], order_data['delivery_date'], 'Pending')
            )
            conn.commit()
            flash("Order placed successfully!", "success")
            return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash(f"An error occurred: {e}", "error")  # More informative error messages
        return False 

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
        # Get form data
        # order_data = request.form.to_dict()
        # del order_data['order_date'] 
        order_data = request.form
        # Check for required fields
        if not all(field in order_data for field in ('supermarket_id', 'items', 'order_date', 'delivery_date')):
            flash("Please fill in all required fields.", "error")
            return redirect('/new_order') 

        # Validate date formats and convert to datetime objects
        try:
            order_date = datetime.datetime.strptime(order_data['order_date'], '%Y-%m-%d').date()
            delivery_date = datetime.datetime.strptime(order_data['delivery_date'], '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect('/new_order')

        # Additional validations (e.g., supermarket_id exists, dates are in the future)

        # Process order submission (using order_data dictionary)
        if not add_order_to_database(order_data):
            flash("An error occurred while saving your order. Please try again.", "error")
            return redirect('/new_order')
        else:
            flash("Order placed successfully!", "success")
            return redirect('/')
    else:
        supermarkets = get_supermarkets()
        return render_template('order_form.html', supermarkets=supermarkets)

@app.route('/deliveries')
def view_deliveries():
    db_path = os.path.abspath('logistics.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, supermarkets.name, order_date, delivery_date, delivery_status FROM orders JOIN supermarkets ON orders.supermarket_id = supermarkets.supermarket_id")
        orders = cursor.fetchall()
    print("Orders fetched from database:", orders)  # Add this line
    return render_template('deliveries.html', orders=orders)

from flask import jsonify  # Import for creating JSON responses

@app.route('/api/supermarkets')
def get_supermarkets_api():
    db_path = os.path.abspath('logistics.db')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT supermarket_id, name FROM supermarkets")
        supermarkets = cursor.fetchall()

    # Convert to a list of dictionaries for easy JSON conversion
    supermarket_list = [
        {"id": supermarket[0], "name": supermarket[1]} for supermarket in supermarkets
    ]
    return jsonify(supermarket_list)  # Return a JSON response


if __name__ == '__main__':
    app.run(debug=True) 
