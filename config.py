import os

SECRET_KEY = os.urandom(24)  # Generate a random secret key
DATABASE_PATH = os.path.abspath('logistics.db')