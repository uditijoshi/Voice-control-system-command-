from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from gui.login_window import LoginWindow
from gui.dashboard import UserDashboard
from gui.admin_panel import AdminPanel
from security.auth import AuthSystem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Banking System")
        self.setGeometry(100, 100, 900, 600)
        
        self.auth_system = AuthSystem()
        self.current_user = None
        self.is_admin = False
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main window UI"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Header
        self.header = QLabel("Smart Banking System")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.header)
        
        # Status bar
        self.status_label = QLabel("Not logged in")
        self.status_label.setStyleSheet("font-size: 12px; color: gray;")
        self.main_layout.addWidget(self.status_label)
        
        # Main content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)
        
        # Show login window initially
        self.show_login()
    
    def show_login(self):
        """Show the login window"""
        self.clear_content()
        self.login_window = LoginWindow(self)
        self.content_layout.addWidget(self.login_window)
        
        # Connect signals
        self.login_window.login_success.connect(self.on_login_success)
    
    def show_dashboard(self):
        """Show the user dashboard"""
        self.clear_content()
        
        if self.is_admin:
            self.dashboard = AdminPanel(self)
        else:
            self.dashboard = UserDashboard(self)
        
        self.content_layout.addWidget(self.dashboard)
        
        # Connect logout signal
        self.dashboard.logout_requested.connect(self.on_logout)
    
    def clear_content(self):
        """Clear the content area"""
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        self.current_user = user_data['user']
        self.is_admin = user_data['is_admin']
        self.status_label.setText(f"Logged in as: {self.current_user['username']}")
        self.show_dashboard()
    
    def on_logout(self):
        """Handle logout"""
        self.auth_system.logout(self.current_user.get('session_id', ''))
        self.current_user = None
        self.is_admin = False
        self.status_label.setText("Not logged in")
        self.show_login()
    
    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
    
    def show_info(self, message):
        """Show information message"""
        QMessageBox.information(self, "Information", message)