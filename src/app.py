from flask import Flask, request, jsonify
from celery.result import AsyncResult
import logging
import os
from tasks import get_train_status
from celery_config import celery as celery_app

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

@app.route('/train-status', methods=['GET'])
def get_train_status_route():
    """
    Get train status endpoint
    
    Query Parameters:
        train_number: The train number to check
        day: Day selection (1 for today, 2 for yesterday, etc.)
        
    Returns:
        JSON response with task ID for async processing
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
        
        # Submit task to Celery
        task = get_train_status.delay(train_number, day)
        
        return jsonify({
            'task_id': task.id,
            'status': 'Processing',
            'status_url': f'/task-status/{task.id}'
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Get the status of a task
    
    Args:
        task_id: The ID of the task to check
        
    Returns:
        JSON response with task status and result if available
    """
    try:
        # Get task result using Celery's AsyncResult
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            'task_id': task_id,
            'status': task_result.state
        }
        
        if task_result.state == 'PENDING':
            response['message'] = 'Task is queued'
        elif task_result.state == 'STARTED':
            response['message'] = 'Task is running'
        elif task_result.state == 'SUCCESS':
            if task_result.result:
                response.update({
                    'result': task_result.result,
                    'message': 'Task completed successfully'
                })
            else:
                response['message'] = 'Task completed but no result available'
        elif task_result.state == 'FAILURE':
            response.update({
                'message': 'Task failed',
                'error': str(task_result.result) if task_result.result else 'Unknown error'
            })
        elif task_result.state == 'RETRY':
            response['message'] = 'Task is being retried'
        else:
            response['message'] = f'Task is in {task_result.state} state'
            
        return jsonify(response)
            
    except Exception as e:
        logger.error(f"Error checking task status: {str(e)}")
        return jsonify({
            'task_id': task_id,
            'status': 'ERROR',
            'error': 'Failed to check task status',
            'message': str(e)
        }), 500
    
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        celery_ping = celery_app.control.ping(timeout=1.0)
        celery_status = 'connected' if celery_ping else 'disconnected'
    except Exception:
        celery_status = 'error'

    return jsonify({
        'status': 'healthy',
        'celery_status': celery_status
    })

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    app.run(host='0.0.0.0', port=5001) 