import mysql.connector
from config import DB_CONFIG
from datetime import datetime
from threading import Lock, Semaphore
from .accounts import AccountManager

# Limiting concurrent transaction processing
transaction_semaphore = Semaphore(5)  # Allow 5 concurrent transactions
transaction_lock = Lock()

class TransactionManager:
    @staticmethod
    def record_transaction(account_id, transaction_type, amount, description=None, related_account=None):
        """Record a transaction in the database"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO transactions 
                (account_id, transaction_type, amount, description, related_account, status)
                VALUES (%s, %s, %s, %s, %s, 'PENDING')
            """, (account_id, transaction_type.upper(), amount, description, related_account))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            
            # Add to transaction queue for processing
            cursor.execute("""
                INSERT INTO transaction_queue (transaction_id)
                VALUES (%s)
            """, (transaction_id,))
            conn.commit()
            
            return transaction_id
        except mysql.connector.Error as err:
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def process_transactions():
        """Process pending transactions (to be run in a separate thread)"""
        while True:
            transaction_semaphore.acquire()
            
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            try:
                with transaction_lock:
                    # Get next transaction from queue
                    cursor.execute("""
                        SELECT t.transaction_id, t.account_id, t.transaction_type, 
                               t.amount, t.related_account, a.account_number
                        FROM transaction_queue q
                        JOIN transactions t ON q.transaction_id = t.transaction_id
                        JOIN accounts a ON t.account_id = a.account_id
                        WHERE q.status = 'QUEUED'
                        ORDER BY q.added_at ASC
                        LIMIT 1
                        FOR UPDATE
                    """)
                    
                    transaction = cursor.fetchone()
                    
                    if not transaction:
                        transaction_semaphore.release()
                        continue
                    
                    # Mark as processing
                    cursor.execute("""
                        UPDATE transaction_queue
                        SET status = 'PROCESSING'
                        WHERE queue_id = (
                            SELECT queue_id FROM transaction_queue
                            WHERE transaction_id = %s
                            LIMIT 1
                        )
                    """, (transaction['transaction_id'],))
                    conn.commit()
                
                # Process the transaction
                result = TransactionManager._execute_transaction(
                    transaction['account_id'],
                    transaction['transaction_type'],
                    transaction['amount'],
                    transaction['related_account'],
                    transaction['account_number']
                )
                
                # Update transaction status
                with transaction_lock:
                    status = 'COMPLETED' if result else 'FAILED'
                    cursor.execute("""
                        UPDATE transactions
                        SET status = %s
                        WHERE transaction_id = %s
                    """, (status, transaction['transaction_id']))
                    
                    cursor.execute("""
                        UPDATE transaction_queue
                        SET status = %s
                        WHERE transaction_id = %s
                    """, (status, transaction['transaction_id']))
                    
                    conn.commit()
                    
            except mysql.connector.Error as err:
                conn.rollback()
                print(f"Transaction processing error: {err}")
            finally:
                cursor.close()
                conn.close()
                transaction_semaphore.release()
    
    @staticmethod
    def _execute_transaction(account_id, transaction_type, amount, related_account, account_number):
        """Execute the actual transaction logic"""
        if transaction_type == 'DEPOSIT':
            return AccountManager.update_balance(account_number, amount)
        elif transaction_type == 'WITHDRAWAL':
            return AccountManager.update_balance(account_number, -amount)
        elif transaction_type == 'TRANSFER_OUT':
            # This is handled in the transfers module
            return True
        else:
            return False
    
    @staticmethod
    def get_transaction_history(account_id, limit=10):
        """Get transaction history for an account"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT transaction_id, transaction_type, amount, description, 
                       related_account, status, created_at
                FROM transactions
                WHERE account_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (account_id, limit))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            return None
        finally:
            cursor.close()
            conn.close()