import mysql.connector
from config import DB_CONFIG, APP_CONFIG
from .hashing import verify_password
import time
import os
from threading import Lock
import hashlib

# Session management
active_sessions = {}
session_lock = Lock()

class AuthSystem:
    def __init__(self):
        self.login_attempts = {}
    
    def login(self, username, password):
        """Authenticate user with username and password"""
        # Check login attempts
        if username in self.login_attempts:
            attempts, last_attempt = self.login_attempts[username]
            if attempts >= APP_CONFIG['max_login_attempts']:
                if time.time() - last_attempt < 3600:  # 1 hour lockout
                    return False, "Account locked. Too many failed attempts."
                else:
                    del self.login_attempts[username]  # Reset after lockout period
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT user_id, username, password_hash, salt, is_admin 
                FROM users 
                WHERE username = %s
            """, (username,))
            user = cursor.fetchone()
            
            if not user:
                self._record_failed_attempt(username)
                return False, "Invalid username or password"
            
            # Verify password
            if verify_password(user['password_hash'], user['salt'], password):
                # Create session
                session_id = self._create_session(user)
                
                # Reset login attempts
                if username in self.login_attempts:
                    del self.login_attempts[username]
                
                return True, {"session_id": session_id, "is_admin": user['is_admin']}
            else:
                self._record_failed_attempt(username)
                return False, "Invalid username or password"
                
        except mysql.connector.Error as err:
            return False, f"Database error: {err}"
        finally:
            cursor.close()
            conn.close()
    
    def logout(self, session_id):
        """Terminate user session"""
        with session_lock:
            if session_id in active_sessions:
                del active_sessions[session_id]
                return True
            return False
    
    def validate_session(self, session_id):
        """Check if session is valid"""
        with session_lock:
            if session_id in active_sessions:
                session = active_sessions[session_id]
                if time.time() - session['last_activity'] <= APP_CONFIG['session_timeout']:
                    # Update last activity time
                    session['last_activity'] = time.time()
                    return True, session['user']
                else:
                    # Session expired
                    del active_sessions[session_id]
            return False, None
    
    def _create_session(self, user):
        """Create a new session for authenticated user"""
        session_id = hashlib.sha256(os.urandom(60)).hexdigest()
        
        with session_lock:
            active_sessions[session_id] = {
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'is_admin': user['is_admin']
                },
                'last_activity': time.time()
            }
        
        return session_id
    
    def _record_failed_attempt(self, username):
        """Record failed login attempt"""
        if username in self.login_attempts:
            attempts, _ = self.login_attempts[username]
            self.login_attempts[username] = (attempts + 1, time.time())
        else:
            self.login_attempts[username] = (1, time.time())