import sys

import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from os_concepts.multithreading import BankingThreads
import mysql.connector
from config import DB_CONFIG


def initialize_application():
   
    print("Initializing application components...")
    # Check database connection
    try:
        print("hello")
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()
        print("Database connection successful")
        return True
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        print("Please ensure MySQL is running and the database is properly configured.")
        return False

if __name__ == "__main__":
    print("1. Starting application...")
    
    print("2. Initializing application...")
    if not initialize_application():
        print("3. Initialization failed!")
        sys.exit(1)
    
    print("4. Creating QApplication...")
    app = QApplication(sys.argv)
    
    print("5. Starting threads...")
    thread_manager = BankingThreads()
    thread_manager.start_transaction_processors(3)
    
    print("6. Creating main window...")
    window = MainWindow()
    
    print("7. Showing window...")
    window.show()
    
    # Clean up when application exits
    def cleanup():
        print("Cleaning up threads...")
        thread_manager.stop_all()
    
    app.aboutToQuit.connect(cleanup)
    
    print("8. Entering event loop...")
    sys.exit(app.exec_())