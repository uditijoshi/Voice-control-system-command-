from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from security.auth import AuthSystem

class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_system = AuthSystem()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the login UI"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Title
        title = QLabel("Login to Smart Banking")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)
        
        # Form
        form = QWidget()
        form_layout = QFormLayout()
        form.setLayout(form_layout)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        
        self.layout.addWidget(form)
        
        # Buttons
        buttons = QWidget()
        buttons_layout = QHBoxLayout()
        buttons.setLayout(buttons_layout)
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.show_register_dialog)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.register_button)
        
        self.layout.addWidget(buttons)
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password")
            return
        
        success, result = self.auth_system.login(username, password)
        
        if success:
            self.login_success.emit(result)
        else:
            QMessageBox.critical(self, "Login Failed", result)
    
    def show_register_dialog(self):
        """Show user registration dialog"""
        dialog = QWidget()
        dialog.setWindowTitle("Register New User")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        form = QWidget()
        form_layout = QFormLayout()
        form.setLayout(form_layout)
        
        self.reg_username = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.reg_fullname = QLineEdit()
        self.reg_email = QLineEdit()
        
        form_layout.addRow("Username:", self.reg_username)
        form_layout.addRow("Password:", self.reg_password)
        form_layout.addRow("Confirm Password:", self.reg_confirm)
        form_layout.addRow("Full Name:", self.reg_fullname)
        form_layout.addRow("Email:", self.reg_email)
        
        layout.addWidget(form)
        
        buttons = QWidget()
        buttons_layout = QHBoxLayout()
        buttons.setLayout(buttons_layout)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(lambda: self.handle_register(dialog))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(register_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addWidget(buttons)
        
        dialog.show()
    
    def handle_register(self, dialog):
        """Handle user registration"""
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()
        confirm = self.reg_confirm.text().strip()
        fullname = self.reg_fullname.text().strip()
        email = self.reg_email.text().strip()
        
        if not all([username, password, confirm, fullname, email]):
            QMessageBox.warning(dialog, "Input Error", "All fields are required")
            return
        
        if password != confirm:
            QMessageBox.warning(dialog, "Input Error", "Passwords do not match")
            return
        
        # In a real application, you would call your user registration function here
        # For now, we'll just show a success message
        QMessageBox.information(dialog, "Registration", 
                              "Registration request submitted. An admin will activate your account.")
        dialog.close()