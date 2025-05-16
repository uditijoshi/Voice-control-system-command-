import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DB_CONFIG
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from os_concepts.multithreading import BankingThreads
import mysql.connector

def initialize_application():
    print("Initializing application components...")
    try:
        print("Checking database connection...")
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()
        print("Database connection successful.")
        return True
    except mysql.connector.Error as err:
        print(f"[!] Database connection error: {err}")
        return False

if __name__ == "__main__":
    print("Starting application...")
    if not initialize_application():
        print("Exiting due to database error.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
