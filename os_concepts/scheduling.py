import mysql.connector
from config import DB_CONFIG
import time
from queue import PriorityQueue
from threading import Thread, Lock
import random

class TransactionScheduler:
    def __init__(self):
        self.scheduling_algorithms = {
            'FIFO': self._fifo_scheduling,
            'PRIORITY': self._priority_scheduling,
            'ROUND_ROBIN': self._round_robin_scheduling
        }
        self.current_algorithm = 'FIFO'
        self.scheduler_thread = None
        self.stop_event = False
        self.lock = Lock()
    
    def set_scheduling_algorithm(self, algorithm):
        """Set the scheduling algorithm to use"""
        with self.lock:
            if algorithm.upper() in self.scheduling_algorithms:
                self.current_algorithm = algorithm.upper()
                return True
            return False
    
    def start_scheduler(self):
        """Start the transaction scheduler thread"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return False
        
        self.stop_event = False
        self.scheduler_thread = Thread(
            target=self._run_scheduler,
            daemon=True,
            name="TransactionScheduler"
        )
        self.scheduler_thread.start()
        return True
    
    def stop_scheduler(self):
        """Stop the transaction scheduler"""
        self.stop_event = True
        if self.scheduler_thread:
            self.scheduler_thread.join()
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while not self.stop_event:
            with self.lock:
                algorithm = self.scheduling_algorithms[self.current_algorithm]
            
            # Get next transaction based on scheduling algorithm
            transaction = algorithm()
            
            if transaction:
                self._process_transaction(transaction)
            else:
                time.sleep(1)  # No transactions to process
    
    def _fifo_scheduling(self):
        """First-In-First-Out scheduling"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT t.transaction_id, t.account_id, t.transaction_type, 
                       t.amount, t.related_account, a.account_number
                FROM transaction_queue q
                JOIN transactions t ON q.transaction_id = t.transaction_id
                JOIN accounts a ON t.account_id = a.account_id
                WHERE q.status = 'QUEUED'
                ORDER BY q.added_at ASC
                LIMIT 1
            """)
            return cursor.fetchone()
        except mysql.connector.Error:
            return None
        finally:
            cursor.close()
            conn.close()
    
    def _priority_scheduling(self):
        """Priority-based scheduling"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT t.transaction_id, t.account_id, t.transaction_type, 
                       t.amount, t.related_account, a.account_number,
                       q.priority
                FROM transaction_queue q
                JOIN transactions t ON q.transaction_id = t.transaction_id
                JOIN accounts a ON t.account_id = a.account_id
                WHERE q.status = 'QUEUED'
                ORDER BY q.priority DESC, q.added_at ASC
                LIMIT 1
            """)
            return cursor.fetchone()
        except mysql.connector.Error:
            return None
        finally:
            cursor.close()
            conn.close()
    
    def _round_robin_scheduling(self):
        """Round-robin scheduling among accounts"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get the next account in round-robin fashion
            cursor.execute("""
                SELECT a.account_number
                FROM accounts a
                JOIN (
                    SELECT DISTINCT account_id
                    FROM transaction_queue q
                    JOIN transactions t ON q.transaction_id = t.transaction_id
                    WHERE q.status = 'QUEUED'
                ) AS active_accounts ON a.account_id = active_accounts.account_id
                ORDER BY a.last_processed ASC
                LIMIT 1
            """)
            
            account = cursor.fetchone()
            if not account:
                return None
            
            # Get the oldest transaction for this account
            cursor.execute("""
                SELECT t.transaction_id, t.account_id, t.transaction_type, 
                       t.amount, t.related_account, a.account_number
                FROM transaction_queue q
                JOIN transactions t ON q.transaction_id = t.transaction_id
                JOIN accounts a ON t.account_id = a.account_id
                WHERE q.status = 'QUEUED' AND a.account_number = %s
                ORDER BY q.added_at ASC
                LIMIT 1
            """, (account['account_number'],))
            
            transaction = cursor.fetchone()
            
            if transaction:
                # Update last processed time for the account
                cursor.execute("""
                    UPDATE accounts
                    SET last_processed = NOW()
                    WHERE account_number = %s
                """, (account['account_number'],))
                conn.commit()
            
            return transaction
        except mysql.connector.Error:
            return None
        finally:
            cursor.close()
            conn.close()
    
    def _process_transaction(self, transaction):
        """Process a transaction (simplified version)"""
        from banking.transactions import TransactionManager
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        try:
            # Mark as processing
            cursor.execute("""
                UPDATE transaction_queue
                SET status = 'PROCESSING'
                WHERE transaction_id = %s
            """, (transaction['transaction_id'],))
            conn.commit()
            
            # Simulate processing time
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            # Mark as completed
            cursor.execute("""
                UPDATE transaction_queue
                SET status = 'COMPLETED'
                WHERE transaction_id = %s
            """, (transaction['transaction_id'],))
            
            cursor.execute("""
                UPDATE transactions
                SET status = 'COMPLETED'
                WHERE transaction_id = %s
            """, (transaction['transaction_id'],))
            
            conn.commit()
            
        except mysql.connector.Error as err:
            conn.rollback()
            print(f"Error processing transaction: {err}")
        finally:
            cursor.close()
            conn.close()
    
    def demo_scheduling_algorithms(self):
        """Demonstrate different scheduling algorithms"""
        print("\n=== Scheduling Algorithms Demo ===")
        
        # Create test transactions
        from banking.accounts import AccountManager
        from banking.transactions import TransactionManager
        
        # Create test accounts
        AccountManager.create_account(1, 'SAVINGS', 1000.00)
        accounts = AccountManager.get_accounts(1)
        account_number = accounts[0]['account_number']
        
        # Add test transactions with different priorities
        for i in range(10):
            amount = random.randint(1, 100)
            transaction_id = TransactionManager.record_transaction(
                accounts[0]['account_id'],
                'DEPOSIT',
                amount,
                f"Test transaction {i+1}"
            )
            
            # Set random priorities for some transactions
            if i % 2 == 0:
                priority = random.randint(1, 10)
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE transaction_queue
                    SET priority = %s
                    WHERE transaction_id = %s
                """, (priority, transaction_id))
                conn.commit()
                cursor.close()
                conn.close()
        
        # Test FIFO scheduling
        print("\nFIFO Scheduling:")
        self.set_scheduling_algorithm('FIFO')
        self._test_scheduler(5)
        
        # Test Priority scheduling
        print("\nPriority Scheduling:")
        self.set_scheduling_algorithm('PRIORITY')
        self._test_scheduler(5)
        
        # Test Round Robin scheduling
        print("\nRound Robin Scheduling:")
        self.set_scheduling_algorithm('ROUND_ROBIN')
        self._test_scheduler(5)
    
    def _test_scheduler(self, num_transactions):
        """Test the current scheduling algorithm"""
        for _ in range(num_transactions):
            with self.lock:
                algorithm = self.scheduling_algorithms[self.current_algorithm]
            
            transaction = algorithm()
            if transaction:
                print(f"Processing transaction {transaction['transaction_id']} "
                      f"(Amount: {transaction['amount']}, "
                      f"Account: {transaction['account_number']})")
                self._process_transaction(transaction)
            else:
                print("No transactions to process")
                break
