import mysql.connector
from config import DB_CONFIG
from .accounts import AccountManager
from .transactions import TransactionManager
from threading import Lock, Semaphore
import time

# Transfer locks to prevent deadlocks
transfer_lock = Lock()
account_locks = {}  # Dictionary to store locks for each account
lock_dict_lock = Lock()  # To protect account_locks dictionary

class TransferManager:
    @staticmethod
    def initiate_transfer(sender_account_id, receiver_account_number, amount, description=None):
        """Initiate a fund transfer between accounts"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get sender account details
            cursor.execute("""
                SELECT a.account_id, a.account_number, a.balance, u.user_id
                FROM accounts a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.account_id = %s
            """, (sender_account_id,))
            sender = cursor.fetchone()
            
            if not sender:
                return False, "Sender account not found"
            
            # Check if sender has sufficient balance
            if sender['balance'] < amount:
                return False, "Insufficient funds"
            
            # Get receiver account details
            cursor.execute("""
                SELECT account_id, account_number, user_id
                FROM accounts
                WHERE account_number = %s
            """, (receiver_account_number,))
            receiver = cursor.fetchone()
            
            if not receiver:
                return False, "Receiver account not found"
            
            if sender['account_id'] == receiver['account_id']:
                return False, "Cannot transfer to the same account"
            
            # Record the outgoing transaction
            transaction_id = TransactionManager.record_transaction(
                sender['account_id'],
                'TRANSFER_OUT',
                amount,
                description,
                receiver_account_number
            )
            
            if not transaction_id:
                return False, "Failed to record transaction"
            
            # Record the incoming transaction for receiver
            TransactionManager.record_transaction(
                receiver['account_id'],
                'TRANSFER_IN',
                amount,
                description,
                sender['account_number']
            )
            
            # Execute the transfer
            success = TransferManager._execute_transfer(
                sender['account_number'],
                receiver['account_number'],
                amount
            )
            
            if not success:
                return False, "Transfer failed"
            
            return True, "Transfer completed successfully"
            
        except mysql.connector.Error as err:
            return False, f"Database error: {err}"
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def _execute_transfer(sender_account, receiver_account, amount):
        """Execute the actual transfer with proper locking to avoid deadlocks"""
        # Get locks for both accounts (ordered to prevent deadlocks)
        account1, account2 = sorted([sender_account, receiver_account])
        
        # Get or create locks for these accounts
        with lock_dict_lock:
            if account1 not in account_locks:
                account_locks[account1] = Lock()
            if account2 not in account_locks:
                account_locks[account2] = Lock()
            
            lock1 = account_locks[account1]
            lock2 = account_locks[account2]
        
        # Acquire locks in consistent order
        lock1.acquire()
        lock2.acquire()
        
        try:
            # Deduct from sender
            if not AccountManager.update_balance(sender_account, -amount):
                return False
            
            # Add to receiver
            if not AccountManager.update_balance(receiver_account, amount):
                # Revert sender deduction if receiver update fails
                AccountManager.update_balance(sender_account, amount)
                return False
            
            return True
        finally:
            # Release locks
            lock2.release()
            lock1.release()
    
    @staticmethod
    def get_transfer_history(user_id):
        """Get transfer history for a user"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT t.transaction_id, t.transaction_type, t.amount, 
                       t.description, t.related_account, t.status, t.created_at,
                       a.account_number
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.user_id = %s 
                AND t.transaction_type IN ('TRANSFER_IN', 'TRANSFER_OUT')
                ORDER BY t.created_at DESC
            """, (user_id,))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            return None
        finally:
            cursor.close()
            conn.close()