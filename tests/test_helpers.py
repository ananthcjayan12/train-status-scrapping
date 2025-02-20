"""Tests for helper utilities"""

import unittest
from datetime import datetime
from src.utils.helpers import calculate_date, validate_train_number, format_delay_status

class TestHelpers(unittest.TestCase):
    """Test cases for helper functions"""
    
    def test_validate_train_number(self):
        """Test train number validation"""
        self.assertTrue(validate_train_number("12345"))
        self.assertFalse(validate_train_number("123"))
        self.assertFalse(validate_train_number("abcde"))
        self.assertFalse(validate_train_number("123456"))
    
    def test_format_delay_status(self):
        """Test delay status formatting"""
        self.assertEqual(format_delay_status("-"), "On time")
        self.assertEqual(format_delay_status(""), "On time")
        self.assertEqual(format_delay_status("10 mins"), "10 mins")
        self.assertEqual(format_delay_status(" 5 mins "), "5 mins")
    
    def test_calculate_date(self):
        """Test date calculation"""
        today = datetime.now()
        self.assertEqual(
            calculate_date(1),
            today.strftime("%d-%m-%Y")
        )
        
if __name__ == "__main__":
    unittest.main() 