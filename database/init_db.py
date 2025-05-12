import mysql.connector
from config import DB_CONFIG
import os

def initialize_database():
    try:
        # Connect to MySQL server (without specifying a database)
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Check if database exists
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
        
        # Create database
        cursor.execute("CREATE DATABASE smart_banking")
        print("Database created successfully.")
        
        # Read and execute schema file
        with open(os.path.join(os.path.dirname(__file__), 'banking_schema.sql'), 'r') as f:
            sql_commands = f.read().split(';')
            
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
        
        print("Tables created successfully.")
        
        # Create admin user
        from security.hashing import generate_hash
        admin_username = "admin"
        admin_password = "admin123"
        salt, password_hash = generate_hash(admin_password)
        
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, full_name, email, is_admin)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (admin_username, password_hash, salt, "Administrator", "admin@bank.com"))
        
        conn.commit()
        print("Admin user created (username: admin, password: admin123)")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    initialize_database()