# Transfers module
import sqlite3
from config import DB_CONFIG, DB_TYPE
from .accounts import AccountManager
from threading import Lock

transfer_lock = Lock()

class TransferManager:
    @staticmethod
    def transfer_funds(source_account, destination_account, amount, description=None):
        """Transfer funds between accounts"""
        if amount <= 0:
            return False, "Transfer amount must be greater than zero"
        
        # Get source account balance
        source_balance = AccountManager.get_account_balance(source_account)
        if source_balance is None:
            return False, "Source account not found"
        
        if source_balance < amount:
            return False, "Insufficient funds in source account"
        
        # Verify destination account exists
        dest_balance = AccountManager.get_account_balance(destination_account)
        if dest_balance is None:
            return False, "Destination account not found"
        
        # Start transaction
        conn = None
        cursor = None
        
        try:
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                cursor = conn.cursor()
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
            
            # Use a lock to prevent race conditions
            with transfer_lock:
                # Deduct from source account
                result = AccountManager.update_balance(source_account, -amount)
                if not result:
                    conn.rollback()
                    return False, "Failed to update source account"
                
                # Add to destination account
                result = AccountManager.update_balance(destination_account, amount)
                if not result:
                    # Roll back the source account deduction
                    AccountManager.update_balance(source_account, amount)
                    conn.rollback()
                    return False, "Failed to update destination account"
                
                # Record transactions in transfer history
                placeholder = "?" if DB_TYPE == 'sqlite' else "%s"
                
                # Record debit from source account
                cursor.execute(f"""
                    INSERT INTO transfer_history 
                    (source_account, destination_account, amount, description, transaction_type)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 'OUTGOING')
                """, (source_account, destination_account, amount, description))
                
                # Record credit to destination account
                cursor.execute(f"""
                    INSERT INTO transfer_history 
                    (source_account, destination_account, amount, description, transaction_type)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 'INCOMING')
                """, (source_account, destination_account, amount, description))
                
                conn.commit()
                return True, "Transfer completed successfully"
        
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Transfer error: {str(e)}"
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_transfer_history(account_number, limit=10):
        """Get transfer history for an account"""
        conn = None
        cursor = None
        
        try:
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM transfer_history
                    WHERE source_account = ? OR destination_account = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (account_number, account_number, limit))
                
                return cursor.fetchall()
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT * FROM transfer_history
                    WHERE source_account = %s OR destination_account = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (account_number, account_number, limit))
                
                return cursor.fetchall()
                
        except Exception as e:
            return None
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    @staticmethod
    def create_transfer_history_table():
        """Create the transfer_history table if it doesn't exist"""
        conn = None
        cursor = None
        
        try:
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transfer_history (
                        transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_account TEXT NOT NULL,
                        destination_account TEXT NOT NULL,
                        amount REAL NOT NULL,
                        description TEXT,
                        transaction_type TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transfer_history (
                        transfer_id INT AUTO_INCREMENT PRIMARY KEY,
                        source_account VARCHAR(20) NOT NULL,
                        destination_account VARCHAR(20) NOT NULL,
                        amount DECIMAL(15,2) NOT NULL,
                        description TEXT,
                        transaction_type VARCHAR(10) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                
            return True
        
        except Exception as e:
            return False
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()