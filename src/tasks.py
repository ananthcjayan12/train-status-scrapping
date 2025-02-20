from celery_config import celery
from train_status_scraper import TrainStatusScraper
import logging
from celery.signals import worker_process_init, worker_process_shutdown
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

logger = get_task_logger(__name__)
scraper_instance = None

@worker_process_init.connect
def init_worker(**kwargs):
    """Initialize TrainStatusScraper when worker starts"""
    global scraper_instance
    try:
        scraper_instance = TrainStatusScraper()
        logger.info("Initialized TrainStatusScraper for worker")
    except Exception as e:
        logger.error(f"Failed to initialize TrainStatusScraper: {e}")
        raise

@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    """Cleanup TrainStatusScraper when worker shuts down"""
    global scraper_instance
    if scraper_instance:
        try:
            scraper_instance.cleanup()
            logger.info("Cleaned up TrainStatusScraper for worker")
        except Exception as e:
            logger.error(f"Error cleaning up TrainStatusScraper: {e}")

@celery.task(
    bind=True,
    name='get_train_status',
    queue='train_status',
    rate_limit='30/m',  # Limit to 30 tasks per minute total
    max_retries=3,
    default_retry_delay=5,
    soft_time_limit=240,
    time_limit=300,
    acks_late=True,
    reject_on_worker_lost=True
)
def get_train_status(self, train_number: str, day: int) -> dict:
    """
    Celery task to get train status
    
    Args:
        train_number (str): The train number to check
        day (int): Day selection (1 for today, 2 for yesterday, etc.)
        
    Returns:
        dict: Train status information
    """
    global scraper_instance
    
    try:
        if not scraper_instance:
            logger.info("Creating new TrainStatusScraper instance")
            scraper_instance = TrainStatusScraper()
            
        result = scraper_instance.get_train_status(train_number, day)
        return {
            'status': 'success',
            'data': result,
            'task_id': self.request.id
        }
        
    except SoftTimeLimitExceeded:
        logger.error("Task exceeded soft time limit")
        return {
            'status': 'error',
            'error': 'Task timed out',
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        # If there's a ChromeDriver error, cleanup and create new instance
        try:
            if scraper_instance:
                scraper_instance.cleanup()
            scraper_instance = TrainStatusScraper()
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup/reinit: {cleanup_error}")
            
        raise self.retry(exc=e) 