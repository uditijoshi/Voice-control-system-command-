import sqlite3
import mysql.connector
from config import DB_CONFIG, DB_TYPE, APP_CONFIG
from .hashing import verify_password, generate_hash
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
        
        try:
            if DB_TYPE == 'sqlite':
                # SQLite connection
                conn = sqlite3.connect(DB_CONFIG['database'])
                conn.row_factory = sqlite3.Row  # This enables dictionary-like access
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id, username, password_hash, salt, is_admin, full_name, email 
                    FROM users 
                    WHERE username = ?
                """, (username,))
                user = cursor.fetchone()
            else:
                # MySQL connection
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT user_id, username, password_hash, salt, is_admin, full_name, email 
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
                
                # Return user data
                user_info = {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'is_admin': user['is_admin'],
                    'session_id': session_id
                }
                
                return True, {
                    'user': user_info,
                    'is_admin': user['is_admin']
                }
            else:
                self._record_failed_attempt(username)
                return False, "Invalid username or password"
                
        except Exception as err:
            return False, f"Database error: {err}"
        finally:
            cursor.close()
            conn.close()
    
    def register_user(self, username, password, fullname, email, is_admin=False):
        """Register a new user in the database"""
        try:
            # Generate password hash and salt
            salt, password_hash = generate_hash(password)
            
            if DB_TYPE == 'sqlite':
                # Check if users table exists, if not create it
                conn = sqlite3.connect(DB_CONFIG['database'])
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE users (
                            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password_hash TEXT NOT NULL,
                            salt TEXT NOT NULL,
                            full_name TEXT NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            is_admin BOOLEAN NOT NULL DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    conn.commit()
                
                # Check if username already exists
                cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    return False, "Username already exists"
                
                # Check if email already exists
                cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    return False, "Email already registered"
                
                # Insert new user
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, full_name, email, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, password_hash, salt, fullname, email, 1 if is_admin else 0))
                conn.commit()
                
            else:
                # MySQL connection
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                # Check if username already exists
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return False, "Username already exists"
                
                # Check if email already exists
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return False, "Email already registered"
                
                # Insert new user
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, full_name, email, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (username, password_hash, salt, fullname, email, 1 if is_admin else 0))
                conn.commit()
            
            return True, "User registered successfully"
            
        except Exception as err:
            return False, f"Registration error: {err}"
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
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
