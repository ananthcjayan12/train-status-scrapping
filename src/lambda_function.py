from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os
import logging
from train_status_scraper import TrainStatusScraper
import chromium.chromium_binary  # Lambda layer will provide this

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def init_chrome_options():
    """Initialize Chrome options for Lambda environment"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-dev-tools')
    chrome_options.add_argument('--no-zygote')
    chrome_options.add_argument('--user-data-dir=/tmp/chrome-user-data')
    chrome_options.binary_location = '/opt/chrome/chrome'
    return chrome_options

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: API Gateway event containing query parameters
        context: Lambda context
        
    Returns:
        API Gateway response object
    """
    try:
        # Extract parameters from event
        params = event.get('queryStringParameters', {})
        if not params:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameters'
                })
            }
            
        train_number = params.get('train_number')
        day = int(params.get('day', 1))
        
        if not train_number:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: train_number'
                })
            }
            
        if not (1 <= day <= 5):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Day parameter must be between 1 and 5'
                })
            }

        # Initialize scraper with Lambda-specific Chrome options
        scraper = TrainStatusScraper(chrome_options=init_chrome_options())
        
        try:
            # Get train status
            result = scraper.get_train_status(train_number, day)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'data': result
                })
            }
            
        finally:
            # Ensure cleanup
            scraper.cleanup()
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        } 