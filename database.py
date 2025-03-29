import mysql.connector

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "samarth@2006",
    "database": "users",
}

def connect_db():
    """Establishes and returns a connection to the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None

def store_user(user_id, name, gender, age, height=None, weight=None, password=""):
    """Inserts a new user into the database with name, gender, age, height, weight, and password."""
    if user_exists(user_id):  
        print(f"[DEBUG] User {user_id} already exists. Skipping insertion.")
        return  
    try:
        conn = connect_db()
        if not conn:
            print("[ERROR] Database connection failed.")  
            return
        cursor = conn.cursor()
        query = """
            INSERT INTO user (user_id, name, gender, age, height, weight, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, name, gender, age, height, weight, password))  
        conn.commit()
        print(f"[SUCCESS] User {user_id} inserted.")  
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"[ERROR] Database Error in store_user(): {err}")


def store_password(user_id, password):
    """Stores the user's password in the database."""
    if not user_exists(user_id):  
        print(f"[ERROR] User {user_id} does not exist. Cannot store password.")  
        return
    try:
        conn = connect_db()
        if not conn:
            print("[ERROR] Database connection failed.")  
            return
        cursor = conn.cursor()
        query = "UPDATE user SET password = %s WHERE user_id = %s"
        cursor.execute(query, (password, user_id))  
        conn.commit()
        print(f"[SUCCESS] Password for User {user_id} updated.")  
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"[ERROR] Database Error in store_password(): {err}")

def user_exists(user_id):
    """Checks if a user already exists in the database."""
    try:
        conn = connect_db()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return False
