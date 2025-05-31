import sqlite3
import mysql.connector
from config import DB_CONFIG, DB_TYPE

class DatabaseAdapter:
    @staticmethod
    def get_connection():
        """Get a database connection based on the configured DB_TYPE"""
        if DB_TYPE == 'sqlite':
            conn = sqlite3.connect(DB_CONFIG['database'])
            conn.row_factory = sqlite3.Row
            return conn
        else:
            return mysql.connector.connect(**DB_CONFIG)
    
    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False, dictionary=False):
        """Execute a database query with the appropriate placeholders"""
        conn = None
        cursor = None
        result = None
        
        try:
            if DB_TYPE == 'sqlite':
                conn = sqlite3.connect(DB_CONFIG['database'])
                if dictionary:
                    conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Replace %s with ? for SQLite
                query = query.replace("%s", "?")
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.lastrowid
                
                if commit:
                    conn.commit()
                
            else:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=dictionary)
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.lastrowid
                
                if commit:
                    conn.commit()
            
            return result
            
        except Exception as e:
            if conn and commit:
                conn.rollback()
            raise e
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_placeholder():
        """Get the appropriate placeholder for the current DB_TYPE"""
        return "?" if DB_TYPE == 'sqlite' else "%s" 