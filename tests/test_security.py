import unittest
from security.hashing import generate_hash, verify_password

class TestSecurity(unittest.TestCase):
    """Test security and authentication components"""
    
    def test_password_hashing(self):
        """Test that password hashing and verification works"""
        password = "securepassword123"
        salt, pwdhash = generate_hash(password)
        
        # Should verify correct password
        self.assertTrue(verify_password(pwdhash, salt, password))
        
        # Should reject wrong password
        self.assertFalse(verify_password(pwdhash, salt, "wrongpassword"))
        
        # Different salts should produce different hashes
        _, newhash = generate_hash(password)
        self.assertNotEqual(pwdhash, newhash)

if __name__ == '__main__':
    unittest.main()