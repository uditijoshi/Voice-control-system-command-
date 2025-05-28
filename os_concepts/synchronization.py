import threading
import time
import random
from banking.accounts import AccountManager

class SynchronizationDemo:
    def __init__(self):
        self.mutex = threading.Lock()
        self.semaphore = threading.Semaphore(3)  # Allow 3 concurrent
        