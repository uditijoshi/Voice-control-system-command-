import mysql.connector
from config import DB_CONFIG
import os

def initialize_database():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()

        cursor.execute("SHOW DATABASES LIKE 'smart_banking'")
        result = cursor.fetchone()
        if result:
            print("Database already exists. Do you want to recreate it? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                cursor.execute("DROP DATABASE smart_banking")
                print("Existing database dropped.")
            else:
                print("Using existing database.")
                return

        cursor.execute("CREATE DATABASE smart_banking")
        print("Database created.")

        conn.database = 'smart_banking'

        schema_path = os.path.join(os.path.dirname(__file__), 'banking_schema.sql')
        with open(schema_path, 'r') as f:
            sql_script = f.read()
            for result in cursor.execute(sql_script, multi=True):
                pass
        print("Tables created successfully.")

        from security.hashing import generate_hash
        salt, password_hash = generate_hash("admin123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, full_name, email, is_admin)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, ("admin", password_hash, salt, "Administrator", "admin@bank.com"))
        conn.commit()
        print("Admin user created.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    initialize_database()
