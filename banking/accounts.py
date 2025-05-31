# Accounts module
import sqlite3
import random
import string
from threading import Lock
from config import DB_CONFIG, DB_TYPE
import time

account_lock = Lock()

class AccountManager:
    @staticmethod
    def create_account(user_id, account_type, initial_balance=0.0):
        """Create a new account for a user"""
        try:
            # Generate a unique account number
            account_number = ''.join(random.choices(string.digits, k=12))
            
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO accounts (user_id, account_number, account_type, balance)
                    VALUES (?, ?, ?, ?)
                """, (user_id, account_number, account_type, initial_balance))
                
                conn.commit()
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO accounts (user_id, account_number, account_type, balance)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, account_number, account_type, initial_balance))
                
                conn.commit()
            
            return True, account_number
        
        except Exception as err:
            return False, str(err)
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    @staticmethod
    def get_accounts(user_id):
        """Get all accounts for a user"""
        try:
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM accounts WHERE user_id = ?
                    ORDER BY created_at DESC
                """, (user_id,))
                
                accounts = cursor.fetchall()
                return [dict(account) for account in accounts]
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT * FROM accounts WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                
                return cursor.fetchall()
        
        except Exception as err:
            print(f"Error getting accounts: {err}")
            return None
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    @staticmethod
    def get_account_balance(account_number):
        """Get the balance of an account"""
        try:
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT balance FROM accounts WHERE account_number = ?
                """, (account_number,))
                
                result = cursor.fetchone()
                return result[0] if result else None
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT balance FROM accounts WHERE account_number = %s
                """, (account_number,))
                
                result = cursor.fetchone()
                return result[0] if result else None
        
        except Exception as err:
            print(f"Error getting account balance: {err}")
            return None
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    @staticmethod
    def update_balance(account_number, amount_change):
        """Update the balance of an account"""
        try:
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance + ? 
                    WHERE account_number = ?
                """, (amount_change, account_number))
                
                conn.commit()
                return cursor.rowcount > 0
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance + %s 
                    WHERE account_number = %s
                """, (amount_change, account_number))
                
                conn.commit()
                return cursor.rowcount > 0
        
        except Exception as err:
            print(f"Error updating account balance: {err}")
            return False
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def link_external_bank_account(user_id, bank_name, account_number, account_holder_name, ifsc_code=None):
        """Link an external bank account to a user profile"""
        try:
            # Create the linked_bank_accounts table if it doesn't exist
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                cursor = conn.cursor()
                
                # Create table if it doesn't exist
                cursor.execute("""
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
                """)
                
                # Insert the linked bank account
                cursor.execute("""
                    INSERT INTO linked_bank_accounts 
                    (user_id, bank_name, account_number, account_holder_name, ifsc_code)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, bank_name, account_number, account_holder_name, ifsc_code))
                
                conn.commit()
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                # Create table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS linked_bank_accounts (
                        link_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        bank_name VARCHAR(100) NOT NULL,
                        account_number VARCHAR(50) NOT NULL,
                        account_holder_name VARCHAR(100) NOT NULL,
                        ifsc_code VARCHAR(20),
                        is_verified TINYINT DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        UNIQUE(user_id, account_number)
                    )
                """)
                
                # Insert the linked bank account
                cursor.execute("""
                    INSERT INTO linked_bank_accounts 
                    (user_id, bank_name, account_number, account_holder_name, ifsc_code)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, bank_name, account_number, account_holder_name, ifsc_code))
                
                conn.commit()
            
            # In a real app, here we would initiate a verification process
            # For demo purposes, we'll simulate a successful verification
            AccountManager.verify_external_bank_account(user_id, account_number)
            
            return True, "Bank account linked successfully"
        
        except Exception as err:
            return False, f"Error linking bank account: {str(err)}"
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    @staticmethod
    def verify_external_bank_account(user_id, account_number):
        """Verify an external bank account (in a real app, this would involve micro-deposits)"""
        try:
            # In a real app, this would be a complex process involving:
            # 1. Making small deposits to the account (e.g., $0.32, $0.45)
            # 2. User verifying the deposit amounts
            # 3. Marking the account as verified
            
            # For demo purposes, we'll just mark it as verified after a short delay
            time.sleep(1)  # Simulate verification process
            
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE linked_bank_accounts 
                    SET is_verified = 1
                    WHERE user_id = ? AND account_number = ?
                """, (user_id, account_number))
                
                conn.commit()
                return cursor.rowcount > 0
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE linked_bank_accounts 
                    SET is_verified = 1
                    WHERE user_id = %s AND account_number = %s
                """, (user_id, account_number))
                
                conn.commit()
                return cursor.rowcount > 0
        
        except Exception as err:
            print(f"Error verifying bank account: {err}")
            return False
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    @staticmethod
    def get_linked_bank_accounts(user_id):
        """Get all linked external bank accounts for a user"""
        try:
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='linked_bank_accounts'")
                if not cursor.fetchone():
                    return []
                
                cursor.execute("""
                    SELECT * FROM linked_bank_accounts WHERE user_id = ?
                    ORDER BY created_at DESC
                """, (user_id,))
                
                accounts = cursor.fetchall()
                return [dict(account) for account in accounts]
            else:
                import mysql.connector
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                
                # Check if table exists
                cursor.execute("SHOW TABLES LIKE 'linked_bank_accounts'")
                if not cursor.fetchone():
                    return []
                
                cursor.execute("""
                    SELECT * FROM linked_bank_accounts WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                
                return cursor.fetchall()
        
        except Exception as err:
            print(f"Error getting linked bank accounts: {err}")
            return None
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()