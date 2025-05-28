from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QMessageBox,
                            QCheckBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QBrush, QPalette, QPixmap, QPainter, QPainterPath
from security.auth import AuthSystem
import re
import os

class GradientFrame(QFrame):
    def __init__(self, color1="#6a11cb", color2="#2575fc", parent=None):
        super().__init__(parent)
        self.color1 = color1
        self.color2 = color2
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(self.color1))
        gradient.setColorAt(1.0, QColor(self.color2))
        
        painter.fillRect(self.rect(), QBrush(gradient))

class RoundedButton(QPushButton):
    def __init__(self, text, color1="#6a11cb", color2="#2575fc", parent=None):
        super().__init__(text, parent)
        self.color1 = color1
        self.color2 = color2
        self.setMinimumHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor(self.color1))
        gradient.setColorAt(1.0, QColor(self.color2))
        
        # Create rounded rect path
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
        # Fill with gradient
        painter.setClipPath(path)
        painter.fillPath(path, QBrush(gradient))
        
        # Draw text
        painter.setPen(QColor("white"))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_system = AuthSystem()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the login UI"""
        # Set the main window style with gradient background
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #000000;
            }
        """)
        
        # Create main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(25)
        self.setLayout(self.layout)
        
        # Create gradient background
        self.background = GradientFrame("#8E2DE2", "#4A00E0")
        self.background.setObjectName("background")
        
        # Set layout for background
        bg_layout = QVBoxLayout()
        bg_layout.setContentsMargins(0, 0, 0, 0)
        self.background.setLayout(bg_layout)
        
        # Add decorative elements - circles
        for i in range(5):
            circle = QLabel()
            size = 30 + (i * 15)  # Vary the size
            circle.setFixedSize(size, size)
            circle.setStyleSheet(f"""
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: {size/2}px;
            """)
            x_pos = (i * 50) % 300
            y_pos = (i * 40) % 200
            circle.move(x_pos, y_pos)
            circle.setParent(self)
            
        # Bank Logo/Icon with colorful background
        logo_container = QFrame()
        logo_container.setFixedSize(100, 100)
        logo_container.setStyleSheet("""
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
                                      stop:0 #FF9500, stop:1 #FF5E3A);
            border-radius: 50px;
            margin: 0 auto;
        """)
        logo_layout = QVBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_container.setLayout(logo_layout)
        
        logo_label = QLabel("🏦")
        logo_label.setStyleSheet("font-size: 48px; color: white;")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        
        logo_container_wrapper = QHBoxLayout()
        logo_container_wrapper.addStretch()
        logo_container_wrapper.addWidget(logo_container)
        logo_container_wrapper.addStretch()
        
        self.layout.addLayout(logo_container_wrapper)
        
        # Title with colorful text
        title = QLabel("Welcome to Smart Banking")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #000000;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5);
        """)
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Your Financial Journey Starts Here")
        subtitle.setStyleSheet("""
            font-size: 16px; 
            color: #000000;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(subtitle)
        
        # Form container with glass effect
        form_container = QFrame()
        form_container.setFrameShape(QFrame.StyledPanel)
        form_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.9);
            }
        """)
        
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(20)
        form_container.setLayout(form_layout)
        
        # Add shadow effect to form
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        form_container.setGraphicsEffect(shadow)
        
        # Username input
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #000000;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid rgba(142, 45, 226, 0.5);
                border-radius: 10px;
                padding: 5px 15px;
                background-color: rgba(255, 255, 255, 0.8);
                color: #000000;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #FF9500;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.5);
            }
        """)
        self.username_input.textChanged.connect(self.validate_inputs)
        form_layout.addWidget(self.username_input)
        
        # Password input
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #000000;")
        form_layout.addWidget(password_label)
        
        password_container = QWidget()
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(10)
        password_container.setLayout(password_layout)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid rgba(142, 45, 226, 0.5);
                border-radius: 10px;
                padding: 5px 15px;
                background-color: rgba(255, 255, 255, 0.8);
                color: #000000;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #FF9500;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.5);
            }
        """)
        self.password_input.textChanged.connect(self.validate_inputs)
        password_layout.addWidget(self.password_input)
        
        # Toggle password visibility button
        self.toggle_password_btn = QPushButton("👁️")
        self.toggle_password_btn.setFixedSize(45, 45)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(142, 45, 226, 0.2);
                border: 2px solid rgba(142, 45, 226, 0.5);
                border-radius: 10px;
                font-size: 16px;
                color: #000000;
            }
            QPushButton:hover {
                background-color: rgba(142, 45, 226, 0.3);
                border: 2px solid #FF9500;
            }
        """)
        self.toggle_password_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_btn)
        
        form_layout.addWidget(password_container)
        
        # Remember me and forgot password
        options_container = QWidget()
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_container.setLayout(options_layout)
        
        self.remember_me = QCheckBox("Remember me")
        self.remember_me.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #000000;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 2px solid rgba(142, 45, 226, 0.7);
                background: rgba(255, 255, 255, 0.8);
            }
            QCheckBox::indicator:checked {
                background: #FF9500;
                border: 2px solid #FF9500;
            }
        """)
        options_layout.addWidget(self.remember_me)
        
        forgot_password = QPushButton("Forgot Password?")
        forgot_password.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8E2DE2;
                border: none;
                font-size: 14px;
                text-align: right;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FF5E3A;
                text-decoration: underline;
            }
        """)
        forgot_password.setCursor(Qt.PointingHandCursor)
        forgot_password.clicked.connect(self.forgot_password)
        options_layout.addWidget(forgot_password, alignment=Qt.AlignRight)
        
        form_layout.addWidget(options_container)
        
        # Status message (for validation feedback)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #FF5E3A; font-size: 14px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.status_label)
        
        # Login button with gradient
        self.login_button = RoundedButton("LOGIN", "#FF9500", "#FF5E3A")
        self.login_button.setMinimumHeight(50)
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)
        
        # Register option
        register_container = QWidget()
        register_layout = QHBoxLayout()
        register_layout.setContentsMargins(0, 10, 0, 0)
        register_container.setLayout(register_layout)
        
        register_label = QLabel("Don't have an account?")
        register_label.setStyleSheet("font-size: 14px; color: #000000;")
        register_layout.addWidget(register_label)
        
        register_btn = QPushButton("Register Now")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8E2DE2;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FF5E3A;
                text-decoration: underline;
            }
        """)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.clicked.connect(self.show_register_dialog)
        register_layout.addWidget(register_btn)
        
        form_layout.addWidget(register_container)
        
        self.layout.addWidget(form_container)
        
        # Set initial focus
        self.username_input.setFocus()
        
        # Set initial button state
        self.validate_inputs()
    
    def validate_inputs(self):
        """Validate input fields and update UI accordingly"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.login_button.setEnabled(False)
            self.login_button.setStyleSheet("""
                background-color: rgba(142, 45, 226, 0.3);
                color: rgba(0, 0, 0, 0.5);
                border-radius: 10px;
                padding: 10px;
                font-size: 15px;
                font-weight: bold;
            """)
            if not username and not password:
                self.status_label.setText("")
            elif not username:
                self.status_label.setText("Please enter your username")
            else:
                self.status_label.setText("Please enter your password")
        else:
            self.login_button.setEnabled(True)
            self.status_label.setText("")
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("👁️")
    
    def forgot_password(self):
        """Handle forgot password request"""
        email = QLineEdit()
        email.setPlaceholderText("Enter your email address")
        email.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 15px;
                background-color: white;
                font-size: 14px;
                min-height: 30px;
                color: #000000;
            }
        """)
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Password Recovery")
        msg_box.setText("Enter your email to reset your password:")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        layout = msg_box.layout()
        layout.addWidget(email, 1, 1)
        
        result = msg_box.exec_()
        
        if result == QMessageBox.Ok:
            email_text = email.text().strip()
            if email_text and re.match(r"[^@]+@[^@]+\.[^@]+", email_text):
                QMessageBox.information(self, "Password Recovery", 
                                     "If your email is registered in our system, you will receive password reset instructions shortly.")
            else:
                QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
    
    def handle_login(self):
        """Handle login button click with animation"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.status_label.setText("Please enter both username and password")
            self.shake_animation()
            return
        
        # Show loading state
        original_text = self.login_button.text()
        self.login_button.setText("LOGGING IN...")
        self.login_button.setEnabled(False)
        
        # Use timer to simulate network delay and show the loading state
        QTimer.singleShot(800, lambda: self.process_login(username, password, original_text))
    
    def process_login(self, username, password, original_text):
        """Process the login after showing loading state"""
        try:
            success, result = self.auth_system.login(username, password)
            
            if success:
                self.login_success.emit(result)
            else:
                self.login_button.setText(original_text)
                self.login_button.setEnabled(True)
                self.status_label.setText(result)
                self.shake_animation()
        except Exception as e:
            self.login_button.setText(original_text)
            self.login_button.setEnabled(True)
            self.status_label.setText(f"Login error: {str(e)}")
            self.shake_animation()
    
    def shake_animation(self):
        """Shake animation for failed login"""
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(100)
        self.animation.setLoopCount(3)
        
        pos = self.pos()
        x, y = pos.x(), pos.y()
        
        self.animation.setKeyValueAt(0, pos)
        self.animation.setKeyValueAt(0.25, QPoint(x + 5, y))
        self.animation.setKeyValueAt(0.5, QPoint(x, y))
        self.animation.setKeyValueAt(0.75, QPoint(x - 5, y))
        self.animation.setKeyValueAt(1, pos)
        
        self.animation.start()
    
    def show_register_dialog(self):
        """Show user registration dialog"""
        dialog = QWidget(self, Qt.Window)
        dialog.setWindowTitle("Register New User")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(500)
        dialog.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #8E2DE2, stop:1 #4A00E0);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #000000;
            }
            QLineEdit {
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 8px;
                padding: 8px 15px;
                background-color: rgba(255, 255, 255, 0.8);
                color: #000000;
                font-size: 14px;
                min-height: 35px;
            }
            QLineEdit:focus {
                border: 2px solid #FF9500;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.5);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #FF9500, stop:1 #FF5E3A);
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #FF5E3A, stop:1 #FF9500);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #FF5E3A, stop:1 #FF5E3A);
            }
            QPushButton#cancel-btn {
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton#cancel-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid white;
            }
            QCheckBox {
                color: #000000;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 2px solid rgba(255, 255, 255, 0.7);
                background: rgba(255, 255, 255, 0.8);
            }
            QCheckBox::indicator:checked {
                background: #FF9500;
                border: 2px solid #FF9500;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        dialog.setLayout(layout)
        
        # Title
        title = QLabel("Create Your Account")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #000000; text-align: center;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Join our banking community today")
        subtitle.setStyleSheet("font-size: 16px; color: #000000; text-align: center;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Form
        form = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form.setLayout(form_layout)
        
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Choose a username")
        
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Create a password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Confirm your password")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        
        self.reg_fullname = QLineEdit()
        self.reg_fullname.setPlaceholderText("Enter your full name")
        
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Enter your email address")
        
        form_layout.addRow("<b>Username:</b>", self.reg_username)
        form_layout.addRow("<b>Password:</b>", self.reg_password)
        form_layout.addRow("<b>Confirm Password:</b>", self.reg_confirm)
        form_layout.addRow("<b>Full Name:</b>", self.reg_fullname)
        form_layout.addRow("<b>Email:</b>", self.reg_email)
        
        layout.addWidget(form)
        
        # Terms and conditions
        terms_check = QCheckBox("I agree to the Terms and Conditions")
        terms_check.setStyleSheet("font-size: 14px; color: #000000;")
        layout.addWidget(terms_check)
        
        # Status message
        self.reg_status = QLabel("")
        self.reg_status.setStyleSheet("color: #FF5E3A; font-size: 14px; font-weight: bold;")
        self.reg_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.reg_status)
        
        # Buttons
        buttons = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(15)
        buttons.setLayout(buttons_layout)
        
        register_btn = QPushButton("CREATE ACCOUNT")
        register_btn.setMinimumHeight(45)
        register_btn.clicked.connect(lambda: self.handle_register(dialog, terms_check.isChecked()))
        
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setObjectName("cancel-btn")
        cancel_btn.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(register_btn)
        
        layout.addWidget(buttons)
        
        dialog.show()
    
    def handle_register(self, dialog, terms_accepted):
        """Handle user registration"""
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()
        confirm = self.reg_confirm.text().strip()
        fullname = self.reg_fullname.text().strip()
        email = self.reg_email.text().strip()
        
        # Validate inputs
        if not all([username, password, confirm, fullname, email]):
            self.reg_status.setText("All fields are required")
            return
        
        if not terms_accepted:
            self.reg_status.setText("You must accept the Terms and Conditions")
            return
        
        if password != confirm:
            self.reg_status.setText("Passwords do not match")
            return
        
        if len(password) < 8:
            self.reg_status.setText("Password must be at least 8 characters long")
            return
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.reg_status.setText("Please enter a valid email address")
            return
        
        # Register the user in the database
        success, message = self.auth_system.register_user(username, password, fullname, email)
        
        if success:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Registration Successful")
            msg_box.setText("Your account has been created successfully!")
            msg_box.setInformativeText("You can now login with your new credentials.")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            dialog.close()
        else:
            self.reg_status.setText(message)