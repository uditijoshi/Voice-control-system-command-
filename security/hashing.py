import hashlib
import os
import binascii
import sqlite3
import mysql.connector
from config import DB_CONFIG, DB_TYPE

def generate_hash(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return salt.decode('ascii'), pwdhash.decode('ascii')

def verify_password(stored_hash, stored_salt, provided_password):
    pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                  provided_password.encode('utf-8'), 
                                  stored_salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_hash

def change_password(username, old_password, new_password):
    try:
        if DB_TYPE == 'sqlite':
            # SQLite connection
            conn = sqlite3.connect(DB_CONFIG['database'])
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found."
            
            if not verify_password(user['password_hash'], user['salt'], old_password):
                return False, "Incorrect current password."
            
            new_salt, new_hash = generate_hash(new_password)
            
            cursor.execute("""
                UPDATE users
                SET password_hash = ?, salt = ?
                WHERE username = ?
            """, (new_hash, new_salt, username))
            conn.commit()
            
        else:
            # MySQL connection
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT password_hash, salt FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found."
            
            if not verify_password(user['password_hash'], user['salt'], old_password):
                return False, "Incorrect current password."
            
            new_salt, new_hash = generate_hash(new_password)
            
            cursor.execute("""
                UPDATE users
                SET password_hash = %s, salt = %s
                WHERE username = %s
            """, (new_hash, new_salt, username))
            conn.commit()

        return True, "Password changed successfully."

    except Exception as err:
        return False, f"Database error: {err}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and (
            (DB_TYPE == 'mysql' and conn.is_connected()) or 
            (DB_TYPE == 'sqlite')
        ):
            conn.close()
