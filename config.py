#import os
from pathlib import Path
# Add this at the top of init_db.py:
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'udita@123',
    'database': 'smart_banking',
    'port': 3306
}

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