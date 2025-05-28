import mysql.connector
import os
import sys
import time

# Add parent directory to path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG

def initialize_database():
    # Give MySQL time to fully start up
    print("Waiting for MySQL to start...")
    time.sleep(5)
    
    # First try to connect without specifying a database
    connection_config = DB_CONFIG.copy()
    if 'database' in connection_config:
        del connection_config['database']
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Connecting to MySQL (attempt {retry_count + 1}/{max_retries})...")
            conn = mysql.connector.connect(**connection_config)
            cursor = conn.cursor()
            
            print("Connected to MySQL successfully.")
            
            # Check if database exists
            cursor.execute("SHOW DATABASES LIKE 'smart_banking'")
            result = cursor.fetchone()
            
            if result:
                print("Database 'smart_banking' already exists.")
                choice = input("Do you want to recreate it? (y/n): ").strip().lower()
                if choice == 'y':
                    cursor.execute("DROP DATABASE smart_banking")
                    print("Existing database dropped.")
                else:
                    print("Using existing database.")
                    conn.database = 'smart_banking'
                    return
            
            # Create database
            cursor.execute("CREATE DATABASE smart_banking")
            print("Database 'smart_banking' created successfully.")
            
            # Use the new database
            cursor.execute("USE smart_banking")
            conn.database = 'smart_banking'
            
            # Create tables
            schema_path = os.path.join(os.path.dirname(__file__), 'banking_schema.sql')
            with open(schema_path, 'r') as f:
                sql_script = f.read()
                # Split the script by semicolons to execute each statement separately
                statements = sql_script.split(';')
                for statement in statements:
                    if statement.strip():
                        cursor.execute(statement)
            
            conn.commit()
            print("Tables created successfully.")
            
            # Create admin user
            from security.hashing import generate_hash
            salt, password_hash = generate_hash("admin123")
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, full_name, email, is_admin)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """, ("admin", password_hash, salt, "Administrator", "admin@bank.com"))
            conn.commit()
            print("Admin user created successfully.")
            
            return True
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Maximum retry attempts reached. Could not connect to MySQL.")
                return False
                
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                print("MySQL connection closed.")

if __name__ == "__main__":
    success = initialize_database()
    if success:
        print("Database initialization completed successfully.")
    else:
        print("Database initialization failed.")
        sys.exit(1)
