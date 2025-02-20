"""Helper utilities for train status scraping"""

from datetime import datetime, timedelta

def calculate_date(day_selection: int) -> str:
    """
    Calculate the date based on day selection
    
    Args:
        day_selection (int): Day selection (1 for today, 2 for yesterday, etc.)
        
    Returns:
        str: Formatted date string (DD-MM-YYYY)
    """
    today = datetime.now()
    target_date = today - timedelta(days=day_selection - 1)
    return target_date.strftime("%d-%m-%Y")

def validate_train_number(train_number: str) -> bool:
    """
    Validate train number format
    
    Args:
        train_number (str): Train number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Most Indian train numbers are 5 digits
    return train_number.isdigit() and len(train_number) == 5

def format_delay_status(delay_text: str) -> str:
    """
    Format delay status text
    
    Args:
        delay_text (str): Raw delay status text
        
    Returns:
        str: Formatted delay status
    """
    if not delay_text or delay_text == "-":
        return "On time"
    return delay_text.strip() 