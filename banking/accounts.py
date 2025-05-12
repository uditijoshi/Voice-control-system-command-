import mysql.connector
from config import DB_CONFIG
import random
import string
from threading import Lock

account_lock = Lock()

class AccountManager:
    @staticmethod
    def create_account(user_id, account_type, initial_balance=0.00):
        """Create a new bank account for user"""
        account_number = ''.join(random.choices(string.digits, k=12))
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        try:
            with account_lock:
                cursor.execute("""
                    INSERT INTO accounts (user_id, account_number, account_type, balance)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, account_number, account_type.upper(), initial_balance))
                conn.commit()
                
                return True, account_number
        except mysql.connector.Error as err:
            return False, f"Database error: {err}"
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_accounts(user_id):
        """Get all accounts for a user"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT account_id, account_number, account_type, balance, created_at
                FROM accounts
                WHERE user_id = %s
            """, (user_id,))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_account_balance(account_number):
        """Get current balance of an account"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT balance FROM accounts WHERE account_number = %s
            """, (account_number,))
            result = cursor.fetchone()
            return result['balance'] if result else None
        except mysql.connector.Error as err:
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_balance(account_number, amount):
        """Update account balance (atomic operation)"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        try:
            with account_lock:
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance + %s 
                    WHERE account_number = %s
                """, (amount, account_number))
                
                if cursor.rowcount == 0:
                    conn.rollback()
                    return False
                
                conn.commit()
                return True
        except mysql.connector.Error as err:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()