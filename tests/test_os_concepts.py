import unittest
import threading
import time
from os_concepts.multithreading import BankingThreads
from os_concepts.scheduling import TransactionScheduler

class TestOSConcepts(unittest.TestCase):
    """Test operating system concepts implementation"""
    
    def test_thread_manager(self):
        """Test banking thread manager starts and stops correctly"""
        thread_manager = BankingThreads()
        
        # Test starting threads
        thread_manager.start_transaction_processors(2)
        self.assertEqual(len(thread_manager.threads), 2)
        
        # Verify threads are alive
        for thread in thread_manager.threads:
            self.assertTrue(thread.is_alive())
        
        # Test stopping threads
        thread_manager.stop_all()
        time.sleep(0.1)  # Give threads time to stop
        for thread in thread_manager.threads:
            self.assertFalse(thread.is_alive())
    
    def test_scheduler(self):
        """Test transaction scheduler"""
        scheduler = TransactionScheduler()
        
        # Test algorithm switching
        self.assertTrue(scheduler.set_scheduling_algorithm('FIFO'))
        self.assertTrue(scheduler.set_scheduling_algorithm('PRIORITY'))
        self.assertTrue(scheduler.set_scheduling_algorithm('ROUND_ROBIN'))
        self.assertFalse(scheduler.set_scheduling_algorithm('INVALID'))
        
        # Test thread starts and stops
        scheduler.start_scheduler()
        self.assertTrue(scheduler.scheduler_thread.is_alive())
        
        scheduler.stop_scheduler()
        time.sleep(0.1)
        self.assertFalse(scheduler.scheduler_thread.is_alive())

if __name__ == '__main__':
    unittest.main()