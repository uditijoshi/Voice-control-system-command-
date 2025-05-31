import threading
import time
import random
from queue import Queue
from banking.transactions import TransactionManager

class BankingThreads:
    def __init__(self):
        self.threads = []
        self.stop_event = threading.Event()
    
    def start_transaction_processors(self, num_threads=3):
        """Start multiple threads to process transactions"""
        for i in range(num_threads):
            thread = threading.Thread(
                target=self._transaction_processor_worker,
                name=f"TransactionProcessor-{i+1}",
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
    
    def _transaction_processor_worker(self):
        """Worker function for transaction processing threads"""
        while not self.stop_event.is_set():
            TransactionManager.process_transactions()
            time.sleep(0.1)  # Small delay to prevent CPU overuse
    
    def start_concurrent_transfers_demo(self):
        """Demonstrate concurrent transfers with potential race conditions"""
        print("\n=== Concurrent Transfers Demo ===")
        
        # Create test accounts
        from banking.accounts import AccountManager
        from banking.transfers import TransferManager
        
        # Create two test accounts with initial balances
        AccountManager.create_account(1, 'SAVINGS', 1000.00)
        AccountManager.create_account(2, 'SAVINGS', 1000.00)
        
        accounts = AccountManager.get_accounts(1)
        account1 = accounts[0]['account_number']
        account2 = AccountManager.get_accounts(2)[0]['account_number']
        
        print(f"Account 1: {account1}, Account 2: {account2}")
        print("Initial balances:")
        print(f"Account 1: {AccountManager.get_account_balance(account1)}")
        print(f"Account 2: {AccountManager.get_account_balance(account2)}")
        
        # Function to perform transfers
        def transfer_worker(amount, iterations):
            for _ in range(iterations):
                TransferManager.transfer_funds(account1, account2, amount, "Demo transfer")
                time.sleep(random.uniform(0.01, 0.1))
        
        # Create multiple threads performing transfers
        threads = []
        for i in range(5):
            amount = random.randint(1, 10)
            t = threading.Thread(
                target=transfer_worker,
                args=(amount, 10),
                name=f"TransferWorker-{i+1}"
            )
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Show final balances
        print("\nFinal balances:")
        print(f"Account 1: {AccountManager.get_account_balance(account1)}")
        print(f"Account 2: {AccountManager.get_account_balance(account2)}")
        print("Note how the balances remain consistent despite concurrent transfers")
    
    def stop_all(self):
        """Stop all running threads"""
        self.stop_event.set()
        for thread in self.threads:
            thread.join()
