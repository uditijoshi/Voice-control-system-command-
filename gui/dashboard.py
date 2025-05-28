# Dashboard module
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTabWidget, QTableWidget, 
                            QTableWidgetItem, QLineEdit, QComboBox, 
                            QFormLayout, QMessageBox, QHeaderView, QInputDialog,
                            QScrollArea, QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QDoubleValidator, QIcon, QColor, QPalette, QFont
from banking.accounts import AccountManager
from banking.transfers import TransferManager
import random
import string

class CircularContactButton(QPushButton):
    """Custom button for contacts with circular avatars"""
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.initials = ''.join([n[0].upper() for n in name.split() if n])[:2]
        if not self.initials:
            self.initials = "?"
        
        # Generate a random color for the avatar
        hue = random.randint(0, 359)
        self.avatar_color = QColor.fromHsv(hue, 200, 220)
        
        # Set up button styling
        self.setFixedSize(60, 80)
        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-color: transparent;
                text-align: center;
                padding-top: 60px;
                font-size: 11px;
            }}
        """)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        import math
        from PyQt5.QtGui import QPainter, QBrush, QPen
        from PyQt5.QtCore import QRect
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle
        painter.setBrush(QBrush(self.avatar_color))
        painter.setPen(Qt.NoPen)
        circle_rect = QRect(10, 0, 40, 40)
        painter.drawEllipse(circle_rect)
        
        # Draw text
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(circle_rect, Qt.AlignCenter, self.initials)

class ActionButton(QPushButton):
    """Custom action button with icon and text"""
    def __init__(self, icon_text, label_text, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.label_text = label_text
        
        # Generate a random color for the icon background
        hue = random.randint(0, 359)
        self.icon_color = QColor.fromHsv(hue, 200, 220)
        
        # Set up button styling
        self.setFixedSize(70, 90)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                text-align: center;
                padding-top: 60px;
                font-size: 12px;
            }
        """)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        from PyQt5.QtGui import QPainter, QBrush, QPen
        from PyQt5.QtCore import QRect
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle
        painter.setBrush(QBrush(self.icon_color))
        painter.setPen(Qt.NoPen)
        circle_rect = QRect(15, 0, 40, 40)
        painter.drawRoundedRect(circle_rect, 10, 10)
        
        # Draw icon text
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(circle_rect, Qt.AlignCenter, self.icon_text)
        
        # Draw label text below
        text_rect = QRect(0, 45, 70, 40)
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 9))
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, self.label_text)

class UserDashboard(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.account_manager = AccountManager()
        self.transfer_manager = TransferManager()
        self.user_id = parent.current_user['user_id']
        self.username = parent.current_user['username']
        self.init_ui()
        self.load_accounts()
    
    def init_ui(self):
        """Initialize the dashboard UI"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        
        # Add banner at top
        banner = QFrame()
        banner.setStyleSheet("""
            background-color: #f2f2f7;
            border-radius: 0px;
            padding: 10px;
        """)
        banner_layout = QVBoxLayout(banner)
        
        # Welcome message
        welcome_label = QLabel(f"Welcome, {self.username}")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        banner_layout.addWidget(welcome_label)
        
        self.content_layout.addWidget(banner)
        
        # Quick Actions Section
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            margin: 10px;
        """)
        actions_layout = QVBoxLayout(actions_frame)
        
        # Quick Actions Title
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        actions_layout.addWidget(actions_title)
        
        # Quick Actions Grid
        actions_grid = QGridLayout()
        actions_grid.setSpacing(10)
        
        # Add action buttons
        scan_btn = ActionButton("QR", "Scan QR\ncode")
        scan_btn.clicked.connect(self.show_qr_scanner)
        
        pay_btn = ActionButton("$", "Pay\ncontacts")
        pay_btn.clicked.connect(self.show_transfer_dialog)
        
        phone_btn = ActionButton("📱", "Pay phone\nnumber")
        phone_btn.clicked.connect(self.show_phone_payment)
        
        bank_btn = ActionButton("🏦", "Bank\ntransfer")
        bank_btn.clicked.connect(self.show_transfer_dialog)
        
        actions_grid.addWidget(scan_btn, 0, 0)
        actions_grid.addWidget(pay_btn, 0, 1)
        actions_grid.addWidget(phone_btn, 0, 2)
        actions_grid.addWidget(bank_btn, 0, 3)
        
        upi_btn = ActionButton("UPI", "Pay UPI ID")
        upi_btn.clicked.connect(lambda: self.parent.show_info("UPI feature coming soon"))
        
        self_btn = ActionButton("👤", "Self\ntransfer")
        self_btn.clicked.connect(self.show_self_transfer)
        
        bills_btn = ActionButton("📄", "Pay\nbills")
        bills_btn.clicked.connect(lambda: self.parent.show_info("Bill payment feature coming soon"))
        
        mobile_btn = ActionButton("📲", "Mobile\nrecharge")
        mobile_btn.clicked.connect(lambda: self.parent.show_info("Mobile recharge feature coming soon"))
        
        actions_grid.addWidget(upi_btn, 1, 0)
        actions_grid.addWidget(self_btn, 1, 1)
        actions_grid.addWidget(bills_btn, 1, 2)
        actions_grid.addWidget(mobile_btn, 1, 3)
        
        actions_layout.addLayout(actions_grid)
        self.content_layout.addWidget(actions_frame)
        
        # People Section
        people_frame = QFrame()
        people_frame.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            margin: 10px;
        """)
        people_layout = QVBoxLayout(people_frame)
        
        # People Title
        people_title = QLabel("People")
        people_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        people_layout.addWidget(people_title)
        
        # People Scroll Area for horizontal scrolling
        people_scroll = QScrollArea()
        people_scroll.setWidgetResizable(True)
        people_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        people_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        people_scroll.setMaximumHeight(100)
        people_scroll.setFrameShape(QFrame.NoFrame)
        
        people_container = QWidget()
        people_container_layout = QHBoxLayout(people_container)
        people_container_layout.setSpacing(5)
        
        # Add some dummy contacts
        dummy_contacts = ["John Smith", "Jane Doe", "Alex Wong", "Maria Garcia", 
                         "David Kim", "Sarah Johnson", "Michael Brown", "Emily Davis"]
        
        for contact in dummy_contacts:
            contact_btn = CircularContactButton(contact)
            contact_btn.clicked.connect(lambda _, name=contact: self.show_contact_transfer(name))
            people_container_layout.addWidget(contact_btn)
        
        people_scroll.setWidget(people_container)
        people_layout.addWidget(people_scroll)
        
        self.content_layout.addWidget(people_frame)
        
        # Bank Accounts Section
        bank_accounts_frame = QFrame()
        bank_accounts_frame.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            margin: 10px;
        """)
        bank_accounts_layout = QVBoxLayout(bank_accounts_frame)
        
        # Bank Accounts Title with Add Bank button
        bank_accounts_header = QHBoxLayout()
        bank_accounts_title = QLabel("Your Bank Accounts")
        bank_accounts_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        bank_accounts_header.addWidget(bank_accounts_title)
        
        add_bank_btn = QPushButton("+ Link Bank")
        add_bank_btn.setStyleSheet("""
            background-color: #1a73e8;
            color: white;
            border-radius: 15px;
            padding: 5px 10px;
        """)
        add_bank_btn.clicked.connect(self.link_bank_account)
        bank_accounts_header.addWidget(add_bank_btn, alignment=Qt.AlignRight)
        
        bank_accounts_layout.addLayout(bank_accounts_header)
        
        # Bank accounts list
        self.bank_accounts_container = QVBoxLayout()
        bank_accounts_layout.addLayout(self.bank_accounts_container)
        
        self.content_layout.addWidget(bank_accounts_frame)
        
        # Set the scroll area widget
        scroll_area.setWidget(content_widget)
        self.layout.addWidget(scroll_area)
        
        # Bottom navigation bar
        nav_bar = QFrame()
        nav_bar.setStyleSheet("""
            background-color: white;
            border-top: 1px solid #e0e0e0;
        """)
        nav_bar.setFixedHeight(60)
        
        nav_layout = QHBoxLayout(nav_bar)
        
        home_btn = QPushButton("Home")
        home_btn.setStyleSheet("border: none; font-weight: bold; color: #1a73e8;")
        
        history_btn = QPushButton("History")
        history_btn.setStyleSheet("border: none;")
        history_btn.clicked.connect(self.show_transaction_history)
        
        profile_btn = QPushButton("Profile")
        profile_btn.setStyleSheet("border: none;")
        profile_btn.clicked.connect(lambda: self.parent.show_info("Profile feature coming soon"))
        
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("border: none;")
        logout_btn.clicked.connect(self.logout_requested.emit)
        
        nav_layout.addWidget(home_btn)
        nav_layout.addWidget(history_btn)
        nav_layout.addWidget(profile_btn)
        nav_layout.addWidget(logout_btn)
        
        self.layout.addWidget(nav_bar)
    
    def load_accounts(self):
        """Load user accounts into the UI"""
        # Load linked bank accounts
        self.load_linked_bank_accounts()
    
    def load_linked_bank_accounts(self):
        """Load linked bank accounts into the UI"""
        # Clear existing bank accounts
        for i in reversed(range(self.bank_accounts_container.count())):
            widget = self.bank_accounts_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get linked bank accounts
        bank_accounts = self.account_manager.get_linked_bank_accounts(self.user_id)
        
        if not bank_accounts:
            no_accounts = QLabel("No bank accounts linked. Link your bank account to make real transfers.")
            no_accounts.setStyleSheet("color: gray; padding: 20px;")
            self.bank_accounts_container.addWidget(no_accounts)
            return
        
        # Add bank account cards
        for account in bank_accounts:
            account_card = QFrame()
            account_card.setStyleSheet("""
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
            """)
            
            card_layout = QHBoxLayout(account_card)
            
            # Bank logo/icon
            bank_icon = QLabel("🏦")
            bank_icon.setStyleSheet("font-size: 24px;")
            card_layout.addWidget(bank_icon)
            
            # Account info
            info_layout = QVBoxLayout()
            
            bank_name = QLabel(account['bank_name'])
            bank_name.setStyleSheet("font-weight: bold;")
            
            # Mask account number for security
            masked_number = "•••• " + account['account_number'][-4:]
            account_number = QLabel(masked_number)
            account_number.setStyleSheet("color: gray; font-size: 12px;")
            
            info_layout.addWidget(bank_name)
            info_layout.addWidget(account_number)
            
            card_layout.addLayout(info_layout)
            
            # Verification status
            if account['is_verified']:
                status = QLabel("✓ Verified")
                status.setStyleSheet("color: green; font-weight: bold;")
            else:
                status = QLabel("⚠ Verification Pending")
                status.setStyleSheet("color: orange; font-weight: bold;")
            
            card_layout.addWidget(status, alignment=Qt.AlignRight)
            
            self.bank_accounts_container.addWidget(account_card)
    
    def show_transfer_dialog(self):
        """Show transfer dialog"""
        accounts = self.account_manager.get_accounts(self.user_id)
        bank_accounts = self.account_manager.get_linked_bank_accounts(self.user_id)
        
        if not accounts:
            self.parent.show_error("You need to create an account before making transfers")
            return
        
        # Check if bank accounts are linked
        use_bank_account = False
        if bank_accounts:
            use_bank_account = QMessageBox.question(
                self, "Transfer Method", 
                "Would you like to transfer directly from your linked bank account?",
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes
        
        if use_bank_account:
            self.show_bank_transfer_dialog(bank_accounts)
        else:
            self.show_internal_transfer_dialog(accounts)
    
    def show_internal_transfer_dialog(self, accounts):
        """Show dialog for internal transfers between app accounts"""
        # Get source account
        account_items = [f"{a['account_type']} - {a['account_number']} (${a['balance']:.2f})" for a in accounts]
        source, ok = QInputDialog.getItem(
            self, "Transfer Money", "Select source account:", account_items, 0, False
        )
        
        if not ok:
            return
        
        source_account = accounts[account_items.index(source)]['account_number']
        
        # Get destination account
        dest, ok = QInputDialog.getText(
            self, "Transfer Money", "Enter destination account number:"
        )
        
        if not ok or not dest:
            return
        
        # Get amount
        amount, ok = QInputDialog.getDouble(
            self, "Transfer Money", "Enter amount to transfer:", 0, 0.01, 1000000, 2
        )
        
        if not ok or amount <= 0:
            return
        
        # Get description
        description, ok = QInputDialog.getText(
            self, "Transfer Money", "Enter description (optional):"
        )
        
        if not ok:
            return
        
        # Confirm transfer
        confirm = QMessageBox.question(
            self, "Confirm Transfer", 
            f"Transfer ${amount:.2f} to account {dest}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.transfer_manager.transfer_funds(
                source_account, dest, amount, description
            )
            
            if success:
                self.parent.show_info("Transfer completed successfully")
                self.load_accounts()
            else:
                self.parent.show_error(f"Transfer failed: {message}")
    
    def show_bank_transfer_dialog(self, bank_accounts):
        """Show dialog for transfers from linked bank accounts"""
        # Get source bank account
        bank_items = [f"{a['bank_name']} - •••• {a['account_number'][-4:]}" for a in bank_accounts if a['is_verified']]
        
        if not bank_items:
            self.parent.show_error("No verified bank accounts available")
            return
        
        source, ok = QInputDialog.getItem(
            self, "Bank Transfer", "Select source bank account:", bank_items, 0, False
        )
        
        if not ok:
            return
        
        source_bank_account = bank_accounts[bank_items.index(source)]
        
        # Get destination account
        dest, ok = QInputDialog.getText(
            self, "Bank Transfer", "Enter destination account number:"
        )
        
        if not ok or not dest:
            return
        
        # Get amount
        amount, ok = QInputDialog.getDouble(
            self, "Bank Transfer", "Enter amount to transfer:", 0, 0.01, 1000000, 2
        )
        
        if not ok or amount <= 0:
            return
        
        # Get description
        description, ok = QInputDialog.getText(
            self, "Bank Transfer", "Enter description (optional):"
        )
        
        if not ok:
            return
        
        # Show UPI/Bank transfer confirmation screen
        payment_dialog = QMessageBox(self)
        payment_dialog.setWindowTitle("Bank Transfer")
        payment_dialog.setText(f"Transfer ₹{amount:.2f} from your {source_bank_account['bank_name']} account to {dest}")
        payment_dialog.setInformativeText("In a real app, this would redirect to your bank's payment gateway or UPI interface.")
        payment_dialog.setDetailedText(
            f"Source: {source_bank_account['bank_name']} (•••• {source_bank_account['account_number'][-4:]})\n"
            f"Destination: {dest}\n"
            f"Amount: ₹{amount:.2f}\n"
            f"Description: {description}"
        )
        payment_dialog.setStandardButtons(QMessageBox.Ok)
        payment_dialog.exec_()
        
        # Simulate successful transfer
        self.parent.show_info("Bank transfer initiated successfully")
        
        # In a real app, we would wait for a callback from the payment gateway
        # For demo purposes, we'll just show a success message
    
    def show_contact_transfer(self, contact_name):
        """Show transfer dialog for a specific contact"""
        accounts = self.account_manager.get_accounts(self.user_id)
        
        if not accounts:
            self.parent.show_error("You need to create an account before making transfers")
            return
        
        # Generate a dummy account number for the contact
        contact_account = ''.join(random.choices(string.digits, k=12))
        
        # Get source account
        account_items = [f"{a['account_type']} - {a['account_number']} (${a['balance']:.2f})" for a in accounts]
        source, ok = QInputDialog.getItem(
            self, f"Pay {contact_name}", "Select source account:", account_items, 0, False
        )
        
        if not ok:
            return
        
        source_account = accounts[account_items.index(source)]['account_number']
        
        # Get amount
        amount, ok = QInputDialog.getDouble(
            self, f"Pay {contact_name}", "Enter amount to transfer:", 0, 0.01, 1000000, 2
        )
        
        if not ok or amount <= 0:
            return
        
        # Get description
        description, ok = QInputDialog.getText(
            self, f"Pay {contact_name}", "Enter description (optional):"
        )
        
        if not ok:
            return
        
        # Show a message that this is a demo feature
        self.parent.show_info(f"Demo: Payment of ${amount:.2f} to {contact_name} would be processed here.")
    
    def show_self_transfer(self):
        """Show self-transfer dialog between own accounts"""
        accounts = self.account_manager.get_accounts(self.user_id)
        
        if not accounts or len(accounts) < 2:
            self.parent.show_error("You need at least two accounts to make a self-transfer")
            return
        
        # Get source account
        account_items = [f"{a['account_type']} - {a['account_number']} (${a['balance']:.2f})" for a in accounts]
        source, ok = QInputDialog.getItem(
            self, "Self Transfer", "Select source account:", account_items, 0, False
        )
        
        if not ok:
            return
        
        source_account = accounts[account_items.index(source)]['account_number']
        
        # Get destination account (excluding source)
        dest_items = [item for item in account_items if item != source]
        dest, ok = QInputDialog.getItem(
            self, "Self Transfer", "Select destination account:", dest_items, 0, False
        )
        
        if not ok:
            return
        
        dest_account = accounts[account_items.index(dest)]['account_number']
        
        # Get amount
        amount, ok = QInputDialog.getDouble(
            self, "Self Transfer", "Enter amount to transfer:", 0, 0.01, 1000000, 2
        )
        
        if not ok or amount <= 0:
            return
        
        # Confirm transfer
        confirm = QMessageBox.question(
            self, "Confirm Self Transfer", 
            f"Transfer ${amount:.2f} between your accounts?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.transfer_manager.transfer_funds(
                source_account, dest_account, amount, "Self transfer"
            )
            
            if success:
                self.parent.show_info("Transfer completed successfully")
                self.load_accounts()
            else:
                self.parent.show_error(f"Transfer failed: {message}")
    
    def show_transaction_history(self):
        """Show transaction history"""
        accounts = self.account_manager.get_accounts(self.user_id)
        
        if not accounts:
            self.parent.show_error("No accounts found")
            return
        
        # Get account to show history for
        account_items = [f"{a['account_type']} - {a['account_number']}" for a in accounts]
        selected, ok = QInputDialog.getItem(
            self, "Transaction History", "Select account:", account_items, 0, False
        )
        
        if not ok:
            return
        
        account_number = accounts[account_items.index(selected)]['account_number']
        
        # Get history
        history = self.transfer_manager.get_transfer_history(account_number)
        
        if not history:
            self.parent.show_info("No transaction history found")
            return
        
        # Show history in a dialog
        history_dialog = QMessageBox(self)
        history_dialog.setWindowTitle("Transaction History")
        
        history_text = f"Transaction History for {selected}\n\n"
        
        for transaction in history:
            if transaction['source_account'] == account_number:
                # Outgoing transaction
                history_text += f"TO: {transaction['destination_account']}\n"
                history_text += f"AMOUNT: -${transaction['amount']:.2f}\n"
            else:
                # Incoming transaction
                history_text += f"FROM: {transaction['source_account']}\n"
                history_text += f"AMOUNT: +${transaction['amount']:.2f}\n"
            
            if transaction['description']:
                history_text += f"DESC: {transaction['description']}\n"
            
            history_text += f"DATE: {transaction['created_at']}\n\n"
        
        history_dialog.setText(history_text)
        history_dialog.exec_()
    
    def link_bank_account(self):
        """Show dialog to link a bank account"""
        # Bank name input
        bank_name, ok = QInputDialog.getText(
            self, "Link Bank Account", "Enter bank name:"
        )
        
        if not ok or not bank_name:
            return
        
        # Account number input
        account_number, ok = QInputDialog.getText(
            self, "Link Bank Account", "Enter account number:"
        )
        
        if not ok or not account_number:
            return
        
        # Account holder name input
        account_holder_name, ok = QInputDialog.getText(
            self, "Link Bank Account", "Enter account holder name:"
        )
        
        if not ok or not account_holder_name:
            return
        
        # IFSC code input (for Indian banks)
        ifsc_code, ok = QInputDialog.getText(
            self, "Link Bank Account", "Enter IFSC code (optional):"
        )
        
        if not ok:
            return
        
        # Confirm linking
        confirm = QMessageBox.question(
            self, "Confirm Bank Account Linking", 
            f"Link your {bank_name} account ending in {account_number[-4:]}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.account_manager.link_external_bank_account(
                self.user_id, bank_name, account_number, account_holder_name, ifsc_code
            )
            
            if success:
                self.parent.show_info("Bank account linked successfully")
                self.load_accounts()
            else:
                self.parent.show_error(f"Failed to link bank account: {message}")

    def show_qr_scanner(self):
        """Show QR scanner dialog"""
        self.parent.show_qr_scanner()

    def show_phone_payment(self):
        """Show phone payment dialog"""
        self.parent.show_phone_payment() 