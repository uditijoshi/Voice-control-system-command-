#import os
from pathlib import Path

# Database configuration
DB_TYPE = 'sqlite'  # Options: 'mysql', 'sqlite'

# SQLite database configuration
SQLITE_CONFIG = {
    'database': 'smart_banking.db'
}

# MySQL database configuration (no longer used)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smart_banking',
    'port': 3306
}

# Use the appropriate database configuration
DB_CONFIG = SQLITE_CONFIG if DB_TYPE == 'sqlite' else MYSQL_CONFIG

# Application settings
APP_CONFIG = {
    'secret_key': 'your-secret-key-here',  # For session management
    'session_timeout': 1800,  # 30 minutes in seconds
    'transaction_limit': 10000.00,  # Daily transaction limit
    'max_login_attempts': 3
}

# Path configurations
BASE_DIR = Path(__file__).parent

DATABASE_DIR = BASE_DIR / 'database'
GUI_DIR = BASE_DIR / 'gui'
SECURITY_DIR = BASE_DIR / 'security'
BANKING_DIR = BASE_DIR / 'banking'
OS_CONCEPTS_DIR = BASE_DIR / 'os_concepts'
TESTS_DIR = BASE_DIR / 'tests'