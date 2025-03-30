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
        print(f"[ERROR] Database Connection Error: {err}")
        return None

def store_user(user_id, name, gender, age, height=None, weight=None, password=""):
    """Inserts a new user into the database."""
    if user_exists(user_id):  
        print(f"[DEBUG] User {user_id} already exists. Skipping insertion.")
        return  
    try:
        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        query = """
            INSERT INTO user (user_id, name, gender, age, height, weight, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, name, gender, age, height, weight, password))  
        conn.commit()
        print(f"[SUCCESS] User {user_id} inserted.")  
    except mysql.connector.Error as err:
        print(f"[ERROR] Database Error in store_user(): {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def user_exists(user_id):
    """Checks if a user already exists in the database."""
    try:
        conn = connect_db()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result is not None
    except mysql.connector.Error as err:
        print(f"[ERROR] Database Error in user_exists(): {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_user_info(user_id, field, value):
    """Updates a specific field (height or weight) for a user."""
    valid_fields = {"height", "weight"}  # Allowed fields to update
    if field not in valid_fields:
        print(f"[ERROR] Invalid field: {field}. Allowed fields: {valid_fields}")
        return
    try:
        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        query = f"UPDATE user SET {field} = %s WHERE user_id = %s"
        cursor.execute(query, (value, user_id))
        conn.commit()
        print(f"[SUCCESS] Updated {field} for user {user_id} to {value}.")
    except mysql.connector.Error as err:
        print(f"[ERROR] Database Error in update_user_info(): {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def get_user_password(user_id):
    # Example: Replace with actual MySQL query
    connection = connect_db()  # Ensure you have a function to connect
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM user WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0] if result else None
