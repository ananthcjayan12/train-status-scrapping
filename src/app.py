from flask import Flask, request, jsonify
from train_status_scraper import TrainStatusScraper
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize the scraper
scraper = None

def initialize_scraper():
    """Initialize the scraper if not already initialized"""
    global scraper
    try:
        # Always create a new scraper instance
        if scraper:
            scraper.cleanup()
        scraper = TrainStatusScraper()
        logger.info("Scraper initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize scraper: {str(e)}")
        raise

@app.before_request
def before_request():
    """Ensure scraper is initialized before each request"""
    if request.endpoint != 'health_check':  # Skip for health check endpoint
        initialize_scraper()

@app.route('/train-status', methods=['GET'])
def get_train_status():
    """
    Get train status endpoint
    
    Query Parameters:
        train_number: The train number to check
        day: Day selection (1 for today, 2 for yesterday, etc.)
        
    Returns:
        JSON response with train status information
    """
    try:
        # Get query parameters
        train_number = request.args.get('train_number')
        day = request.args.get('day', default=1, type=int)
        
        # Validate parameters
        if not train_number:
            return jsonify({
                'error': 'Missing required parameter: train_number'
            }), 400
            
        if not (1 <= day <= 5):
            return jsonify({
                'error': 'Day parameter must be between 1 and 5'
            }), 400
        
        # Get train status
        result = scraper.get_train_status(train_number, day)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500
    
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'scraper_initialized': scraper is not None
    })

@app.after_request
def after_request(response):
    """Cleanup scraper after each request"""
    global scraper
    if scraper and request.endpoint != 'health_check':  # Skip for health check endpoint
        try:
            scraper.cleanup()
            logger.info("Scraper cleaned up successfully after request")
            scraper = None
        except Exception as e:
            logger.error(f"Error cleaning up scraper: {str(e)}")
    return response

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    app.run(host='0.0.0.0', port=5001) 