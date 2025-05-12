from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTabWidget, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QMessageBox , QLineEdit , QInputDialog  )
from PyQt5.QtCore import Qt, pyqtSignal
from banking.accounts import AccountManager
from os_concepts.scheduling import TransactionScheduler
from os_concepts.multithreading import BankingThreads
from PyQt5.QtWidgets import QComboBox  # Missing in your imports
import mysql.connector
from config import DB_CONFIG

class AdminPanel(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.account_manager = AccountManager()
        self.scheduler = TransactionScheduler()
        self.thread_manager = BankingThreads()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the admin panel UI"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Header
        header = QLabel("Administrator Dashboard")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # User Management Tab
        self.users_tab = QWidget()
        self.init_users_tab()
        self.tabs.addTab(self.users_tab, "User Management")
        
        # System Monitoring Tab
        self.system_tab = QWidget()
        self.init_system_tab()
        self.tabs.addTab(self.system_tab, "System Monitoring")
        
        # OS Concepts Tab
        self.os_tab = QWidget()
        self.init_os_tab()
        self.tabs.addTab(self.os_tab, "OS Concepts Demo")
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout_requested.emit)
        self.layout.addWidget(logout_btn, alignment=Qt.AlignRight)
    
    def init_users_tab(self):
        """Initialize the user management tab"""
        layout = QVBoxLayout()
        self.users_tab.setLayout(layout)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "User ID", "Username", "Full Name", "Email", "Account Count"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.users_table)
        
        # User actions
        actions = QWidget()
        actions_layout = QHBoxLayout()
        actions.setLayout(actions_layout)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        
        actions_layout.addWidget(refresh_btn)
        
        layout.addWidget(actions)
    
    def init_system_tab(self):
        """Initialize the system monitoring tab"""
        layout = QVBoxLayout()
        self.system_tab.setLayout(layout)
        
        # Transactions queue table
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(6)
        self.queue_table.setHorizontalHeaderLabels([
            "Queue ID", "Transaction ID", "Account", "Amount", "Status", "Added At"
        ])
        self.queue_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.queue_table)
        
        # System controls
        controls = QWidget()
        controls_layout = QHBoxLayout()
        controls.setLayout(controls_layout)
        
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        
        self.stop_btn = QPushButton("Stop Processing")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        
        layout.addWidget(controls)
    
    def init_os_tab(self):
        """Initialize the OS concepts demo tab"""
        layout = QVBoxLayout()
        self.os_tab.setLayout(layout)
        
        # Scheduling algorithm selection
        scheduling_group = QWidget()
        scheduling_layout = QHBoxLayout()
        scheduling_group.setLayout(scheduling_layout)
        
        scheduling_layout.addWidget(QLabel("Scheduling Algorithm:"))
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["FIFO", "PRIORITY", "ROUND_ROBIN"])
        scheduling_layout.addWidget(self.algorithm_combo)
        
        self.set_algorithm_btn = QPushButton("Set Algorithm")
        self.set_algorithm_btn.clicked.connect(self.set_scheduling_algorithm)
        scheduling_layout.addWidget(self.set_algorithm_btn)
        
        layout.addWidget(scheduling_group)
        
        # Demo buttons
        demo_group = QWidget()
        demo_layout = QHBoxLayout()
        demo_group.setLayout(demo_layout)
        
        self.concurrent_demo_btn = QPushButton("Concurrent Transfers Demo")
        self.concurrent_demo_btn.clicked.connect(self.run_concurrent_demo)
        
        self.scheduling_demo_btn = QPushButton("Scheduling Demo")
        self.scheduling_demo_btn.clicked.connect(self.run_scheduling_demo)
        
        demo_layout.addWidget(self.concurrent_demo_btn)
        demo_layout.addWidget(self.scheduling_demo_btn)
        
        layout.addWidget(demo_group)
    
    def load_data(self):
        """Load data into the admin tables"""
        self.load_users()
        self.load_transaction_queue(self.load_data(self))
        """Load data into the admin tables"""
        try:
            self.load_users()
            self.load_transaction_queue()
        except Exception as e:
            self.parent.show_error(f"Failed to load data: {str(e)}")
            # Consider logging the full traceback
    
    def load_users(self):
        """Load all users into the table"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT u.user_id, u.username, u.full_name, u.email, 
                       COUNT(a.account_id) as account_count
                FROM users u
                LEFT JOIN accounts a ON u.user_id = a.user_id
                GROUP BY u.user_id
                ORDER BY u.user_id
            """)
            
            users = cursor.fetchall()
            
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(user['user_id'])))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['username']))
                self.users_table.setItem(row, 2, QTableWidgetItem(user['full_name']))
                self.users_table.setItem(row, 3, QTableWidgetItem(user['email']))
                self.users_table.setItem(row, 4, QTableWidgetItem(str(user['account_count'])))
        
        except mysql.connector.Error as err:
            self.parent.show_error(f"Failed to load users: {err}")
        finally:
            cursor.close()
            conn.close()
    
    def load_transaction_queue(self):
        """Load the transaction queue into the table"""
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT q.queue_id, q.transaction_id, a.account_number, 
                       t.amount, q.status, q.added_at
                FROM transaction_queue q
                JOIN transactions t ON q.transaction_id = t.transaction_id
                JOIN accounts a ON t.account_id = a.account_id
                ORDER BY q.added_at DESC
                LIMIT 50
            """)
            
            queue_items = cursor.fetchall()
            
            self.queue_table.setRowCount(len(queue_items))
            
            for row, item in enumerate(queue_items):
                self.queue_table.setItem(row, 0, QTableWidgetItem(str(item['queue_id'])))
                self.queue_table.setItem(row, 1, QTableWidgetItem(str(item['transaction_id'])))
                self.queue_table.setItem(row, 2, QTableWidgetItem(item['account_number']))
                self.queue_table.setItem(row, 3, QTableWidgetItem(f"${item['amount']:.2f}"))
                self.queue_table.setItem(row, 4, QTableWidgetItem(item['status']))
                self.queue_table.setItem(row, 5, QTableWidgetItem(str(item['added_at'])))
        
        except mysql.connector.Error as err:
            self.parent.show_error(f"Failed to load transaction queue: {err}")
        finally:
            cursor.close()
            conn.close()
    
    def start_processing(self):
        """Start processing transactions"""
        try:
            self.thread_manager.start_transaction_processors(3)
            self.scheduler.start_scheduler()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Processing transactions...")
            self.status_label.setStyleSheet("color: green;")
            self.parent.show_info("Transaction processing started")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
    
    def stop_processing(self):
        """Stop processing transactions"""
        self.thread_manager.stop_all()
        self.scheduler.stop_scheduler()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.parent.show_info("Transaction processing stopped")
    
    def set_scheduling_algorithm(self):
        """Set the scheduling algorithm"""
        algorithm = self.algorithm_combo.currentText()
        if self.scheduler.set_scheduling_algorithm(algorithm):
            self.parent.show_info(f"Scheduling algorithm set to {algorithm}")
        else:
            self.parent.show_error("Failed to set scheduling algorithm")
    
    def run_concurrent_demo(self):
        """Run the concurrent transfers demo"""
        self.thread_manager.start_concurrent_transfers_demo()
        self.parent.show_info("Concurrent transfers demo started. Check console for output.")
    
    def run_scheduling_demo(self):
        """Run the scheduling algorithms demo"""
        self.scheduler.demo_scheduling_algorithms()
        self.parent.show_info("Scheduling demo started. Check console for output.")