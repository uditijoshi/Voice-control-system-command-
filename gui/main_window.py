from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from gui.login_window import LoginWindow
from gui.dashboard import UserDashboard
from gui.admin_panel import AdminPanel
from security.auth import AuthSystem
import time

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
        self.is_admin = bool(self.current_user['is_admin'])  # Ensure it's a boolean
        self.status_label.setText(f"Logged in as: {self.current_user['username']}")
        print(f"User logged in: {self.current_user['username']}, is_admin: {self.is_admin}")
        
        # Check if user has linked bank accounts
        from banking.accounts import AccountManager
        bank_accounts = AccountManager.get_linked_bank_accounts(self.current_user['user_id'])
        
        if not bank_accounts and not self.is_admin:
            # Show bank account linking dialog
            self.show_bank_linking_dialog()
        else:
            # Show dashboard directly
            self.show_dashboard()
    
    def show_bank_linking_dialog(self):
        """Show dialog to link bank account before proceeding to dashboard"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout
        from PyQt5.QtCore import Qt
        from banking.accounts import AccountManager
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Link Your Bank Account")
        dialog.setMinimumSize(500, 400)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Welcome header
        header = QLabel("Welcome to Smart Banking")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Explanation text
        info = QLabel("To get started, please link your existing bank account.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Bank name input
        bank_name = QLineEdit()
        bank_name.setPlaceholderText("e.g., HDFC Bank, SBI, ICICI")
        form_layout.addRow("Bank Name:", bank_name)
        
        # Account number input
        account_number = QLineEdit()
        account_number.setPlaceholderText("Your bank account number")
        form_layout.addRow("Account Number:", account_number)
        
        # Account holder name input
        account_holder = QLineEdit()
        account_holder.setPlaceholderText("Name as it appears on your bank account")
        form_layout.addRow("Account Holder Name:", account_holder)
        
        # IFSC code input
        ifsc_code = QLineEdit()
        ifsc_code.setPlaceholderText("Bank IFSC code (optional)")
        form_layout.addRow("IFSC Code:", ifsc_code)
        
        layout.addLayout(form_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Skip button
        skip_btn = QPushButton("Skip for Now")
        skip_btn.setStyleSheet("padding: 10px;")
        buttons_layout.addWidget(skip_btn)
        
        # Link button
        link_btn = QPushButton("Link Account")
        link_btn.setStyleSheet("background-color: #1a73e8; color: white; padding: 10px; font-weight: bold;")
        buttons_layout.addWidget(link_btn)
        
        layout.addLayout(buttons_layout)
        
        # Status label
        status = QLabel("")
        status.setStyleSheet("color: #d32f2f; margin-top: 10px;")
        status.setAlignment(Qt.AlignCenter)
        layout.addWidget(status)
        
        # Handle link button click
        def on_link():
            if not bank_name.text().strip():
                status.setText("Please enter your bank name")
                return
                
            if not account_number.text().strip():
                status.setText("Please enter your account number")
                return
                
            if not account_holder.text().strip():
                status.setText("Please enter the account holder name")
                return
            
            # Link the bank account
            success, message = AccountManager.link_external_bank_account(
                self.current_user['user_id'],
                bank_name.text().strip(),
                account_number.text().strip(),
                account_holder.text().strip(),
                ifsc_code.text().strip() if ifsc_code.text().strip() else None
            )
            
            if success:
                dialog.accept()
                self.show_dashboard()
            else:
                status.setText(f"Error: {message}")
        
        # Handle skip button click
        def on_skip():
            dialog.reject()
            self.show_dashboard()
        
        # Connect buttons
        link_btn.clicked.connect(on_link)
        skip_btn.clicked.connect(on_skip)
        
        # Show the dialog
        dialog.exec_()
    
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
        
    def show_qr_scanner(self):
        """Show QR code scanner with real camera"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QFormLayout, QDoubleSpinBox
        from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QImage
        from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
        import random
        import os
        import cv2
        import numpy as np
        
        # Create a dialog for the QR scanner
        scanner_dialog = QDialog(self)
        scanner_dialog.setWindowTitle("QR Code Scanner")
        scanner_dialog.setMinimumSize(400, 500)
        
        layout = QVBoxLayout(scanner_dialog)
        
        # Camera view with real camera feed
        class CameraView(QLabel):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setMinimumHeight(300)
                self.setStyleSheet("background-color: #000;")
                
                # Animation properties
                self.scan_line_pos = 0
                self.scan_direction = 1  # 1 = down, -1 = up
                self.scanning = False
                
                # Camera properties
                self.capture = None
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_frame)
                
                # QR detector
                self.qr_detector = cv2.QRCodeDetector()
                
                # Frame processing
                self.current_frame = None
                self.detected_data = None
                self.last_detection_result = "No QR code found"
            
            def start_camera(self):
                """Start the camera capture"""
                # Try to open the camera
                try:
                    self.capture = cv2.VideoCapture(0)  # 0 is usually the built-in webcam
                    if not self.capture.isOpened():
                        return False
                    
                    # Start the timer to update frames
                    self.timer.start(30)  # 30ms = ~33 fps
                    self.scanning = True
                    return True
                except Exception as e:
                    print(f"Camera error: {e}")
                    return False
            
            def stop_camera(self):
                """Stop the camera capture"""
                self.scanning = False
                self.timer.stop()
                if self.capture is not None:
                    self.capture.release()
                    self.capture = None
            
            def update_frame(self):
                """Update the camera frame and detect QR codes"""
                if self.capture is None or not self.capture.isOpened():
                    return
                
                # Read a frame from the camera
                ret, frame = self.capture.read()
                if not ret:
                    return
                
                # Store original frame for display
                original_frame = frame.copy()
                
                # Set detection result for debug mode
                self.last_detection_result = "No QR code found"
                
                # Detect QR codes in the frame
                try:
                    # Try multiple detection methods for better reliability
                    
                    # Method 1: OpenCV QR detector
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Try to enhance the image for better detection
                    # Apply adaptive threshold
                    thresh = cv2.adaptiveThreshold(
                        gray, 255, 
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                        cv2.THRESH_BINARY, 11, 2
                    )
                    
                    # Try detection on both original and thresholded image
                    for img, img_name in [(gray, "grayscale"), (thresh, "threshold")]:
                        data, bbox, _ = self.qr_detector.detectAndDecode(img)
                        
                        # If QR code detected with OpenCV
                        if data:
                            self.last_detection_result = f"OpenCV ({img_name}): {data[:20]}..."
                            if not self.detected_data:
                                self.detected_data = data
                                # Draw a rectangle around the QR code
                                if bbox is not None:
                                    # Convert bbox to integer points
                                    bbox = bbox.astype(int)
                                    # Draw rectangle
                                    cv2.polylines(frame, [bbox], True, (0, 255, 0), 2)
                                    
                                    # Add text with detected data
                                    cv2.putText(
                                        frame, 
                                        f"QR: {data[:20]}...", 
                                        (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 
                                        0.7, (0, 255, 0), 2
                                    )
                                # Process the detected QR code
                                self.process_detected_qr(data)
                                break  # Stop trying other methods
                    
                    # Method 2: Try using ZBar if OpenCV fails (if available)
                    if not data:
                        try:
                            import pyzbar.pyzbar as pyzbar
                            # Try on both original and enhanced images
                            for img, img_name in [(frame, "color"), (gray, "grayscale"), (thresh, "threshold")]:
                                decoded_objects = pyzbar.decode(img)
                                if decoded_objects:
                                    for obj in decoded_objects:
                                        # Get the data
                                        qr_data = obj.data.decode('utf-8')
                                        self.last_detection_result = f"ZBar ({img_name}): {qr_data[:20]}..."
                                        
                                        if not self.detected_data:
                                            self.detected_data = qr_data
                                            
                                            # Draw the rectangle
                                            points = obj.polygon
                                            if points and len(points) > 0:
                                                pts = np.array([[p.x, p.y] for p in points], np.int32)
                                                pts = pts.reshape((-1, 1, 2))
                                                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                                                
                                                # Add text with detected data
                                                cv2.putText(
                                                    frame, 
                                                    f"QR: {qr_data[:20]}...", 
                                                    (10, 30),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 
                                                    0.7, (0, 255, 0), 2
                                                )
                                            
                                            # Process the detected QR code
                                            self.process_detected_qr(qr_data)
                                            break  # Stop after first detection
                                    
                                    if self.detected_data:
                                        break  # Stop trying other image types
                        except ImportError:
                            # pyzbar not available, skip this method
                            self.last_detection_result += " (pyzbar not available)"
                            pass
                        except Exception as e:
                            self.last_detection_result += f" (ZBar error: {str(e)})"
                            pass
                
                except Exception as e:
                    self.last_detection_result = f"Error: {str(e)}"
                    print(f"QR detection error: {e}")
                
                # Draw scanning UI elements
                # Add a green rectangle to show where to position the QR code
                h, w = frame.shape[:2]
                qr_size = min(w, h) // 2
                top_left = ((w - qr_size) // 2, (h - qr_size) // 2)
                bottom_right = (top_left[0] + qr_size, top_left[1] + qr_size)
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                
                # Add text instructions
                cv2.putText(frame, "Position QR code here", 
                           (top_left[0], top_left[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Move scan line for visual effect
                self.scan_line_pos += 3 * self.scan_direction
                if self.scan_line_pos >= self.height() - 20:
                    self.scan_direction = -1
                elif self.scan_line_pos <= 20:
                    self.scan_direction = 1
                
                # Convert the frame to Qt format for display
                # OpenCV uses BGR, Qt uses RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Store the current frame for painting
                self.current_frame = qt_image
                self.update()
            
            def process_detected_qr(self, data):
                """Process the detected QR code data"""
                if not self.scanning:
                    return
                
                # Stop scanning
                self.scanning = False
                
                # Call the parent's callback
                QTimer.singleShot(500, lambda: self.parent().on_qr_detected(data))
            
            def paintEvent(self, event):
                """Paint the camera view with overlays"""
                super().paintEvent(event)
                
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Draw the current frame if available
                if self.current_frame:
                    scaled_image = self.current_frame.scaled(
                        self.width(), self.height(),
                        Qt.KeepAspectRatio
                    )
                    
                    # Center the image
                    x = (self.width() - scaled_image.width()) // 2
                    y = (self.height() - scaled_image.height()) // 2
                    
                    painter.drawImage(x, y, scaled_image)
                
                # Draw scanning frame
                frame_rect = QRect(50, 50, self.width() - 100, self.height() - 100)
                painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
                painter.drawRect(frame_rect)
                
                # Draw corner markers
                corner_size = 20
                painter.setPen(QPen(QColor(0, 255, 0), 3))
                
                # Top-left corner
                painter.drawLine(frame_rect.left(), frame_rect.top(), frame_rect.left() + corner_size, frame_rect.top())
                painter.drawLine(frame_rect.left(), frame_rect.top(), frame_rect.left(), frame_rect.top() + corner_size)
                
                # Top-right corner
                painter.drawLine(frame_rect.right(), frame_rect.top(), frame_rect.right() - corner_size, frame_rect.top())
                painter.drawLine(frame_rect.right(), frame_rect.top(), frame_rect.right(), frame_rect.top() + corner_size)
                
                # Bottom-left corner
                painter.drawLine(frame_rect.left(), frame_rect.bottom(), frame_rect.left() + corner_size, frame_rect.bottom())
                painter.drawLine(frame_rect.left(), frame_rect.bottom(), frame_rect.left(), frame_rect.bottom() - corner_size)
                
                # Bottom-right corner
                painter.drawLine(frame_rect.right(), frame_rect.bottom(), frame_rect.right() - corner_size, frame_rect.bottom())
                painter.drawLine(frame_rect.right(), frame_rect.bottom(), frame_rect.right(), frame_rect.bottom() - corner_size)
                
                # Draw scan line if scanning
                if self.scanning:
                    scan_gradient = QColor(0, 200, 0, 150)
                    painter.setPen(QPen(scan_gradient, 2))
                    painter.drawLine(
                        frame_rect.left(), frame_rect.top() + self.scan_line_pos,
                        frame_rect.right(), frame_rect.top() + self.scan_line_pos
                    )
            
            def closeEvent(self, event):
                """Handle close event"""
                self.stop_camera()
                super().closeEvent(event)
        
        # Create camera view instance
        camera_view = CameraView()
        layout.addWidget(camera_view)
        
        # Status label
        status_label = QLabel("Point camera at a QR code")
        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Scan button
        scan_btn = QPushButton("Start Camera")
        scan_btn.setStyleSheet("background-color: #1a73e8; color: white; padding: 10px; font-size: 16px;")
        buttons_layout.addWidget(scan_btn)
        
        # Toggle flash button
        flash_btn = QPushButton("Toggle Flash")
        flash_btn.setStyleSheet("padding: 8px;")
        buttons_layout.addWidget(flash_btn)
        
        # Debug mode toggle
        debug_btn = QPushButton("Debug Mode: OFF")
        debug_btn.setStyleSheet("padding: 8px; color: #666;")
        debug_btn.setCheckable(True)
        buttons_layout.addWidget(debug_btn)
        
        layout.addLayout(buttons_layout)
        
        # Additional buttons layout
        extra_buttons_layout = QHBoxLayout()
        
        # Load QR from file button
        load_qr_btn = QPushButton("Load QR from File")
        load_qr_btn.setStyleSheet("padding: 8px;")
        extra_buttons_layout.addWidget(load_qr_btn)
        
        layout.addLayout(extra_buttons_layout)
        
        # Debug info label
        debug_label = QLabel("")
        debug_label.setStyleSheet("color: #666; font-family: monospace;")
        debug_label.setWordWrap(True)
        debug_label.setVisible(False)
        layout.addWidget(debug_label)
        
        # Debug mode flag
        scanner_dialog.debug_mode = False
        
        # Function to toggle debug mode
        def toggle_debug_mode():
            scanner_dialog.debug_mode = debug_btn.isChecked()
            if scanner_dialog.debug_mode:
                debug_btn.setText("Debug Mode: ON")
                debug_btn.setStyleSheet("padding: 8px; background-color: #ffcc00; color: black;")
                debug_label.setVisible(True)
                status_label.setText("Debug mode enabled - showing detection info")
            else:
                debug_btn.setText("Debug Mode: OFF")
                debug_btn.setStyleSheet("padding: 8px; color: #666;")
                debug_label.setVisible(False)
                status_label.setText("Debug mode disabled")
        
        debug_btn.clicked.connect(toggle_debug_mode)
        
        # Update the update_frame method to include debug information
        original_update_frame = camera_view.update_frame
        
        def debug_update_frame():
            result = original_update_frame()
            
            # Add debug information if debug mode is enabled
            if scanner_dialog.debug_mode and camera_view.current_frame is not None:
                # Show camera resolution
                h, w = camera_view.current_frame.height(), camera_view.current_frame.width()
                debug_info = f"Camera: {w}x{h}px | "
                
                # Show detection attempts
                if hasattr(camera_view, 'last_detection_result'):
                    debug_info += f"Detection: {camera_view.last_detection_result} | "
                
                # Show frame rate
                if hasattr(camera_view, 'frame_count'):
                    camera_view.frame_count += 1
                else:
                    camera_view.frame_count = 1
                    camera_view.start_time = time.time()
                
                elapsed = time.time() - camera_view.start_time
                if elapsed > 0:
                    fps = camera_view.frame_count / elapsed
                    debug_info += f"FPS: {fps:.1f}"
                
                # Update debug label
                debug_label.setText(debug_info)
            
            return result
        
        # Replace the update_frame method with our debug version
        camera_view.update_frame = debug_update_frame
        
        # Function to handle QR code detection
        def on_qr_detected(data):
            status_label.setText("QR Code detected! Processing...")
            scan_btn.setEnabled(False)
            
            try:
                # Try to parse the data as a UPI payment
                if data.startswith("upi://"):
                    # Parse UPI data
                    import urllib.parse
                    parsed = urllib.parse.urlparse(data)
                    params = dict(urllib.parse.parse_qsl(parsed.query))
                    
                    payee_name = params.get('pn', 'Unknown').replace('%20', ' ')
                    payee_address = params.get('pa', '')
                    amount = float(params.get('am', '0')) if 'am' in params else 0
                    
                    QTimer.singleShot(1000, lambda: show_payment_form("UPI Payment", payee_name, payee_address, amount))
                else:
                    # Handle as generic account transfer
                    QTimer.singleShot(1000, lambda: show_payment_form("QR Payment", "Scanned Recipient", data, 0))
            except Exception as e:
                print(f"Error parsing QR data: {e}")
                status_label.setText(f"Error: Could not process QR code")
                scan_btn.setEnabled(True)
        
        # Connect QR detection handler
        camera_view.parent = lambda: scanner_dialog
        scanner_dialog.on_qr_detected = on_qr_detected
        
        # Function to start camera
        def start_camera():
            status_label.setText("Starting camera...")
            if camera_view.start_camera():
                status_label.setText("Scanning for QR code...")
                scan_btn.setText("Stop Camera")
                scan_btn.clicked.disconnect()
                scan_btn.clicked.connect(stop_camera)
            else:
                status_label.setText("Failed to start camera")
                
                # Fall back to simulated mode if camera fails
                QTimer.singleShot(2000, simulate_qr_scan)
        
        # Function to stop camera
        def stop_camera():
            camera_view.stop_camera()
            status_label.setText("Camera stopped")
            scan_btn.setText("Start Camera")
            scan_btn.clicked.disconnect()
            scan_btn.clicked.connect(start_camera)
        
        # Function to simulate QR scan (fallback)
        def simulate_qr_scan():
            status_label.setText("Using simulated QR scan instead")
            scan_btn.setEnabled(False)
            
            # Generate simulated UPI data
            simulated_data = "upi://pay?pa=example@upi&pn=John%20Doe&am=100.00"
            
            # Process after delay
            QTimer.singleShot(2000, lambda: on_qr_detected(simulated_data))
        
        # Connect scan button
        scan_btn.clicked.connect(start_camera)
        
        # Connect flash button
        flash_btn.clicked.connect(lambda: status_label.setText("Flash not available"))
        
        # Connect dialog close event
        def on_dialog_close():
            camera_view.stop_camera()
        
        scanner_dialog.finished.connect(on_dialog_close)
        
        # Function to show payment form after successful scan
        def show_payment_form(title, recipient_name, recipient_id, suggested_amount):
            camera_view.stop_camera()
            scanner_dialog.accept()
            
            payment_dialog = QDialog(self)
            payment_dialog.setWindowTitle(title)
            payment_dialog.setMinimumSize(400, 300)
            
            layout = QVBoxLayout(payment_dialog)
            
            # Form layout
            form_layout = QFormLayout()
            
            # Recipient info
            recipient_label = QLabel(f"Pay to: {recipient_name}")
            recipient_label.setStyleSheet("font-weight: bold; font-size: 16px;")
            form_layout.addRow(recipient_label)
            
            id_label = QLabel(f"ID: {recipient_id}")
            form_layout.addRow(id_label)
            
            # Amount input
            amount_input = QDoubleSpinBox()
            amount_input.setRange(1, 10000)
            amount_input.setValue(suggested_amount if suggested_amount > 0 else 100.00)
            amount_input.setPrefix("₹ ")
            amount_input.setDecimals(2)
            amount_input.setStyleSheet("font-size: 18px; padding: 8px;")
            form_layout.addRow("Amount:", amount_input)
            
            # Source account selection
            source_combo = QComboBox()
            
            # Get user's bank accounts
            if self.current_user:
                from banking.accounts import AccountManager
                bank_accounts = AccountManager.get_linked_bank_accounts(self.current_user['user_id'])
                
                if bank_accounts:
                    for account in bank_accounts:
                        source_combo.addItem(
                            f"{account['bank_name']} (•••• {account['account_number'][-4:]})",
                            account['account_number']
                        )
                else:
                    source_combo.addItem("No bank accounts linked")
            
            form_layout.addRow("Pay from:", source_combo)
            
            # Note input
            note_input = QLineEdit()
            note_input.setPlaceholderText("Add a note (optional)")
            form_layout.addRow("Note:", note_input)
            
            layout.addLayout(form_layout)
            
            # Pay button
            pay_btn = QPushButton("Pay Now")
            pay_btn.setStyleSheet("background-color: #1a73e8; color: white; padding: 10px; font-size: 16px;")
            layout.addWidget(pay_btn)
            
            # Handle payment
            def process_payment():
                self.show_info(f"Payment of ₹{amount_input.value():.2f} to {recipient_name} initiated successfully!")
                payment_dialog.accept()
            
            pay_btn.clicked.connect(process_payment)
            
            # Show the payment dialog
            payment_dialog.exec_()
        
        # Function to load QR code from file
        def load_qr_from_file():
            from PyQt5.QtWidgets import QFileDialog
            
            # Pause camera if running
            was_scanning = camera_view.scanning
            if was_scanning:
                camera_view.stop_camera()
            
            # Open file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                scanner_dialog,
                "Select QR Code Image",
                "",
                "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if file_path:
                status_label.setText(f"Loading QR from file: {os.path.basename(file_path)}")
                
                try:
                    # Load image
                    image = cv2.imread(file_path)
                    if image is None:
                        raise ValueError("Failed to load image")
                    
                    # Try to detect QR code
                    # Method 1: OpenCV
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    data, bbox, _ = camera_view.qr_detector.detectAndDecode(gray)
                    
                    if data:
                        # Process the detected QR code
                        on_qr_detected(data)
                        return
                    
                    # Method 2: ZBar
                    try:
                        import pyzbar.pyzbar as pyzbar
                        decoded_objects = pyzbar.decode(image)
                        
                        if decoded_objects:
                            qr_data = decoded_objects[0].data.decode('utf-8')
                            on_qr_detected(qr_data)
                            return
                    except ImportError:
                        pass
                    
                    # If we get here, no QR code was detected
                    status_label.setText("No QR code found in the image")
                    
                except Exception as e:
                    status_label.setText(f"Error processing image: {str(e)}")
                    
                # Restart camera if it was running
                if was_scanning:
                    QTimer.singleShot(2000, start_camera)
            else:
                # Restart camera if it was running
                if was_scanning:
                    start_camera()
        
        # Connect load QR button
        load_qr_btn.clicked.connect(load_qr_from_file)
        
        # Show the dialog
        scanner_dialog.exec_()
        
    def show_phone_payment(self):
        """Show phone number payment dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QFormLayout, QDoubleSpinBox, QHBoxLayout
        
        # Create a dialog for phone payment
        phone_dialog = QDialog(self)
        phone_dialog.setWindowTitle("Pay to Phone Number")
        phone_dialog.setMinimumSize(400, 350)
        
        layout = QVBoxLayout(phone_dialog)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Phone number input with country code
        phone_layout = QHBoxLayout()
        
        country_code = QComboBox()
        country_code.addItems(["+91", "+1", "+44", "+61", "+81"])
        country_code.setFixedWidth(70)
        
        phone_number = QLineEdit()
        phone_number.setPlaceholderText("Enter phone number")
        
        phone_layout.addWidget(country_code)
        phone_layout.addWidget(phone_number)
        
        form_layout.addRow("Phone:", phone_layout)
        
        # Contact lookup button
        lookup_btn = QPushButton("Look up in contacts")
        lookup_btn.setStyleSheet("background-color: #f1f1f1; padding: 5px;")
        form_layout.addRow("", lookup_btn)
        
        # Amount input
        amount_input = QDoubleSpinBox()
        amount_input.setRange(1, 10000)
        amount_input.setValue(100)
        amount_input.setPrefix("₹ ")
        amount_input.setDecimals(2)
        amount_input.setStyleSheet("font-size: 18px; padding: 8px;")
        form_layout.addRow("Amount:", amount_input)
        
        # Source account selection
        source_combo = QComboBox()
        
        # Get user's bank accounts
        if self.current_user:
            from banking.accounts import AccountManager
            bank_accounts = AccountManager.get_linked_bank_accounts(self.current_user['user_id'])
            
            if bank_accounts:
                for account in bank_accounts:
                    source_combo.addItem(
                        f"{account['bank_name']} (•••• {account['account_number'][-4:]})",
                        account['account_number']
                    )
            else:
                source_combo.addItem("No bank accounts linked")
        
        form_layout.addRow("Pay from:", source_combo)
        
        # Note input
        note_input = QLineEdit()
        note_input.setPlaceholderText("Add a note (optional)")
        form_layout.addRow("Note:", note_input)
        
        layout.addLayout(form_layout)
        
        # Recent contacts (simulated)
        recent_label = QLabel("Recent phone payments:")
        recent_label.setStyleSheet("margin-top: 10px;")
        layout.addWidget(recent_label)
        
        # Add some dummy recent contacts
        import random
        
        for _ in range(3):
            random_phone = f"+91 {''.join(random.choices('0123456789', k=10))}"
            contact_btn = QPushButton(random_phone)
            contact_btn.setStyleSheet("text-align: left; padding: 5px;")
            layout.addWidget(contact_btn)
            
            # Connect to fill the phone number field
            contact_btn.clicked.connect(lambda _, num=random_phone: phone_number.setText(num.replace("+91 ", "")))
        
        # Pay button
        pay_btn = QPushButton("Pay Now")
        pay_btn.setStyleSheet("background-color: #1a73e8; color: white; padding: 10px; font-size: 16px; margin-top: 10px;")
        layout.addWidget(pay_btn)
        
        # Handle payment
        def process_payment():
            phone = f"{country_code.currentText()} {phone_number.text()}"
            if not phone_number.text():
                self.show_error("Please enter a phone number")
                return
                
            self.show_info(f"Payment of ₹{amount_input.value():.2f} to {phone} initiated successfully!")
            phone_dialog.accept()
        
        pay_btn.clicked.connect(process_payment)
        
        # Handle contact lookup
        def show_contacts():
            self.show_info("Contact lookup would display your contacts here")
        
        lookup_btn.clicked.connect(show_contacts)
        
        # Show the dialog
        phone_dialog.exec_()