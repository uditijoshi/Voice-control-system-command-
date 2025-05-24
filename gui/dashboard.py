from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTabWidget, QTableWidget, 
                            QTableWidgetItem, QLineEdit, QComboBox, 
                            QFormLayout, QMessageBox, QHeaderView ,QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from banking.accounts import AccountManager
from banking.transactions import TransactionManager
from PyQt5.QtGui import QDoubleValidator
from banking.transfers import TransferManager


class UserDashboard(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.account_manager = AccountManager()
        self.transaction_manager = TransactionManager()
        self.transfer_manager = TransferManager()
        self.user_id = parent.current_user['user_id']
        self.init_ui()
        self.load_accounts()
    
    def init_ui(self):
        """Initialize the dashboard UI"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Header
        header = QLabel(f"Welcome, {self.parent.current_user['username']}")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Account Summary Tab
        self.summary_tab = QWidget()
        self.init_summary_tab()
        self.tabs.addTab(self.summary_tab, "Account Summary")
        
        # Transactions Tab
        self.transactions_tab = QWidget()
        self.init_transactions_tab()
        self.tabs.addTab(self.transactions_tab, "Transactions")
        
        # Transfers Tab
        self.transfers_tab = QWidget()
        self.init_transfers_tab()
        self.tabs.addTab(self.transfers_tab, "Transfers")
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout_requested.emit)
        self.layout.addWidget(logout_btn, alignment=Qt.AlignRight)
    
    def init_summary_tab(self):
        """Initialize the account summary tab"""
        layout = QVBoxLayout()
        self.summary_tab.setLayout(layout)
        
        # Account balance table
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(4)
        self.accounts_table.setHorizontalHeaderLabels([
            "Account Number", "Account Type", "Balance", "Created At"
        ])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.accounts_table)
        
        # Account actions
        actions = QWidget()
        actions_layout = QHBoxLayout()
        actions.setLayout(actions_layout)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_accounts)
        
        new_account_btn = QPushButton("Open New Account")
        new_account_btn.clicked.connect(self.open_new_account)
        
        actions_layout.addWidget(refresh_btn)
        actions_layout.addWidget(new_account_btn)
        
        layout.addWidget(actions)
    
    def init_transactions_tab(self):
        """Initialize the transactions tab"""
        layout = QVBoxLayout()
        self.transactions_tab.setLayout(layout)
        
        # Transaction history table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Type", "Amount", "Description", "Related Account", "Status"
        ])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.transactions_table)
        
        # Transaction form
        form = QWidget()
        form_layout = QFormLayout()
        form.setLayout(form_layout)
        
        self.trans_account = QComboBox()
        self.trans_type = QComboBox()
        self.trans_type.addItems(["DEPOSIT", "WITHDRAWAL"])
        self.trans_amount = QLineEdit()
        self.trans_amount.setValidator(QDoubleValidator(0, 1000000, 2))
        self.trans_desc = QLineEdit()
        
        form_layout.addRow("Account:", self.trans_account)
        form_layout.addRow("Type:", self.trans_type)
        form_layout.addRow("Amount:", self.trans_amount)
        form_layout.addRow("Description:", self.trans_desc)
        
        layout.addWidget(form)
        
        # Submit button
        submit_btn = QPushButton("Submit Transaction")
        submit_btn.clicked.connect(self.submit_transaction)
        layout.addWidget(submit_btn)
    
    def init_transfers_tab(self):
        """Initialize the transfers tab"""
        layout = QVBoxLayout()
        self.transfers_tab.setLayout(layout)
        
        # Transfer history table
        self.transfers_table = QTableWidget()
        self.transfers_table.setColumnCount(6)
        self.transfers_table.setHorizontalHeaderLabels([
            "Date", "Direction", "Amount", "Description", "Related Account", "Status"
        ])
        self.transfers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.transfers_table)
        
        # Transfer form
        form = QWidget()
        form_layout = QFormLayout()
        form.setLayout(form_layout)
        
        self.transfer_from = QComboBox()
        self.transfer_to = QLineEdit()
        self.transfer_to.setPlaceholderText("Recipient account number")
        self.transfer_amount = QLineEdit()
        self.transfer_amount.setValidator(QDoubleValidator(0, 1000000, 2))
        self.transfer_desc = QLineEdit()
        
        form_layout.addRow("From Account:", self.transfer_from)
        form_layout.addRow("To Account:", self.transfer_to)
        form_layout.addRow("Amount:", self.transfer_amount)
        form_layout.addRow("Description:", self.transfer_desc)
        
        layout.addWidget(form)
        
        # This is Submit button
        submit_btn = QPushButton("Submit Transfer")
        submit_btn.clicked.connect(self.submit_transfer)
        layout.addWidget(submit_btn)
    
    def load_accounts(self):
        """Load user accounts into the tables"""
        accounts = self.account_manager.get_accounts(self.user_id)
        
        if accounts is None:
            self.parent.show_error("Failed to load accounts")
            return
        
        # Update accounts table
        self.accounts_table.setRowCount(len(accounts))
        for row, account in enumerate(accounts):
            self.accounts_table.setItem(row, 0, QTableWidgetItem(account['account_number']))
            self.accounts_table.setItem(row, 1, QTableWidgetItem(account['account_type']))
            self.accounts_table.setItem(row, 2, QTableWidgetItem(f"${account['balance']:.2f}"))
            self.accounts_table.setItem(row, 3, QTableWidgetItem(str(account['created_at'])))
        
        # This is for Updating the account dropdowns
        self.trans_account.clear()
        self.transfer_from.clear()
        
        for account in accounts:
            self.trans_account.addItem(
                f"{account['account_number']} ({account['account_type']})", 
                account['account_id']
            )
            self.transfer_from.addItem(
                f"{account['account_number']} (${account['balance']:.2f})", 
                account['account_id']
            )
        
        # Load transactions
        self.load_transactions()
        
        # Load transfers
        self.load_transfers()
    
    def load_transactions(self):
        """Load transaction history"""
        if self.trans_account.count() == 0:
            return
        
        account_id = self.trans_account.currentData()
        transactions = self.transaction_manager.get_transaction_history(account_id, 20)
        
        if transactions is None:
            self.parent.show_error("Failed to load transactions")
            return
        
        self.transactions_table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            self.transactions_table.setItem(row, 0, QTableWidgetItem(str(trans['created_at'])))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(trans['transaction_type']))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(f"${trans['amount']:.2f}"))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(trans.get('description', '')))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(trans.get('related_account', '')))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(trans['status']))
    
    def load_transfers(self):
        """Load transfer history"""
        transfers = self.transfer_manager.get_transfer_history(self.user_id)
        
        if transfers is None:
            self.parent.show_error("Failed to load transfers")
            return
        
        self.transfers_table.setRowCount(len(transfers))
        
        for row, transfer in enumerate(transfers):
            self.transfers_table.setItem(row, 0, QTableWidgetItem(str(transfer['created_at'])))
            self.transfers_table.setItem(row, 1, QTableWidgetItem(transfer['transaction_type']))
            self.transfers_table.setItem(row, 2, QTableWidgetItem(f"${transfer['amount']:.2f}"))
            self.transfers_table.setItem(row, 3, QTableWidgetItem(transfer.get('description', '')))
            
            related_account = transfer.get('related_account', '')
            if transfer['transaction_type'] == 'TRANSFER_OUT':
                direction = "To: " + related_account
            else:
                direction = "From: " + related_account
            
            self.transfers_table.setItem(row, 4, QTableWidgetItem(direction))
            self.transfers_table.setItem(row, 5, QTableWidgetItem(transfer['status']))
    
    def open_new_account(self):
        """Open a new account for the user"""
        account_types = ["SAVINGS", "CHECKING", "BUSINESS"]
        
        account_type, ok = QInputDialog.getItem(
            self, "New Account", "Select account type:", 
            account_types, 0, False
        )
        
        if ok and account_type:
            success, result = self.account_manager.create_account(
                self.user_id, account_type
            )
            
            if success:
                self.parent.show_info(f"New {account_type} account created: {result}")
                self.load_accounts()
            else:
                self.parent.show_error(result)
    
    def submit_transaction(self):
        """Submit a new transaction"""
        if self.trans_account.count() == 0:
            self.parent.show_error("No accounts available")
            return
        
        account_id = self.trans_account.currentData()
        trans_type = self.trans_type.currentText()
        amount_text = self.trans_amount.text().strip()
        description = self.trans_desc.text().strip()
        
        if not amount_text:
            self.parent.show_error("Please enter an amount")
            return
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            self.parent.show_error("Invalid amount")
            return
        
        # This is the Record transaction
        transaction_id = self.transaction_manager.record_transaction(
            account_id, trans_type, amount, description
        )
        
        if transaction_id:
            self.parent.show_info("Transaction submitted successfully")
            self.trans_amount.clear()
            self.trans_desc.clear()
            self.load_accounts()
        else:
            self.parent.show_error("Failed to submit transaction")
    
    def submit_transfer(self):
        """Submit a new transfer"""
        if self.transfer_from.count() == 0:
            self.parent.show_error("No accounts available")
            return
        
        from_account_id = self.transfer_from.currentData()
        to_account = self.transfer_to.text().strip()
        amount_text = self.transfer_amount.text().strip()
        description = self.transfer_desc.text().strip()
        
        if not to_account or not amount_text:
            self.parent.show_error("Please fill all required fields")
            return
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            self.parent.show_error("Invalid amount")
            return
        
        # This is  Initiating the transfer
        success, message = self.transfer_manager.initiate_transfer(
            from_account_id, to_account, amount, description
        )
        
        if success:
            self.parent.show_info(message)
            self.transfer_amount.clear()
            self.transfer_desc.clear()
            self.load_accounts()
        else:
            self.parent.show_error(message)
