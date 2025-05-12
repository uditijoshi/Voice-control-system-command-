import hashlib
import os
import binascii
from config import DB_CONFIG
import mysql.connector

def generate_hash(password):
    """Generate a secure hash and salt for the password"""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                 salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt.decode('ascii'), pwdhash.decode('ascii'))

def verify_password(stored_password, stored_salt, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_salt.encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                  provided_password.encode('utf-8'), 
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def change_password(username, old_password, new_password):
    """Change user password with verification"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get current password hash and salt
        cursor.execute("SELECT password_hash, salt FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            return False, "User not found"
        
        # Verify old password
        if not verify_password(user['password_hash'], user['salt'], old_password):
            return False, "Incorrect current password"
        
        # Generate new hash
        new_salt, new_hash = generate_hash(new_password)
        
        # Update in database
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s, salt = %s 
            WHERE username = %s
        """, (new_hash, new_salt, username))
        conn.commit()
        
        return True, "Password changed successfully"
    
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()