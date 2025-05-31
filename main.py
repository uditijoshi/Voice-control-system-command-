import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DB_CONFIG, DB_TYPE
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from os_concepts.multithreading import BankingThreads

def initialize_application():
    print("Initializing application components...")
    try:
        print("Checking database connection...")
        if DB_TYPE == 'sqlite':
            # SQLite connection
            conn = sqlite3.connect(DB_CONFIG['database'])
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            create_tables_if_needed(cursor)
            
            conn.commit()
            conn.close()
            
            # Create transfer history table
            from banking.transfers import TransferManager
            TransferManager.create_transfer_history_table()
        else:
            # MySQL connection
            import mysql.connector
            conn = mysql.connector.connect(**DB_CONFIG)
            conn.close()
            
        print("Database connection successful.")
        return True
    except Exception as err:
        print(f"[!] Database connection error: {err}")
        return False

def create_tables_if_needed(cursor):
    """Create SQLite tables if they don't exist"""
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_number TEXT NOT NULL UNIQUE,
            account_type TEXT NOT NULL,
            balance REAL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    
    # Linked Bank Accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS linked_bank_accounts (
            link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bank_name TEXT NOT NULL,
            account_number TEXT NOT NULL,
            account_holder_name TEXT NOT NULL,
            ifsc_code TEXT,
            is_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, account_number)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            related_account TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
        )
    ''')
    
    # Transaction queue table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_queue (
            queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            priority INTEGER DEFAULT 5,
            status TEXT DEFAULT 'QUEUED',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
        )
    ''')
    
    # Check if admin user exists, if not create one
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        from security.hashing import generate_hash
        salt, password_hash = generate_hash("admin123")
        cursor.execute('''
            INSERT INTO users (username, password_hash, salt, full_name, email, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("admin", password_hash, salt, "Administrator", "admin@bank.com", 1))
        print("Admin user created.")

if __name__ == "__main__":
    print("Starting application...")
    if not initialize_application():
        print("Exiting due to database error.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
