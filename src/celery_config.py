from celery import Celery
from kombu import Exchange, Queue
import os

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_MASTER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
REDIS_REPLICA_URL = os.getenv('REDIS_REPLICA_URL', REDIS_MASTER_URL)

# Define exchange and queue
CELERY_EXCHANGE = Exchange('train_status', type='direct')
CELERY_QUEUE = Queue('train_status', CELERY_EXCHANGE, routing_key='train_status')

# Celery app configuration
app = Celery(
    'train_status',
    include=['tasks']
)

# Configure Celery
app.conf.update(
    # Broker settings - use master for writing
    broker_url=REDIS_MASTER_URL,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_pool_limit=None,

    # Result backend - can use replica for reading results if needed
    result_backend=REDIS_MASTER_URL,  # Use master for both to be safe
    result_serializer='json',
    result_expires=3600,  # Results expire in 1 hour
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    
    # Concurrency settings
    worker_concurrency=3,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    
    # Queue settings
    task_default_queue='train_status',
    task_queues=(CELERY_QUEUE,),
    task_default_exchange='train_status',
    task_default_routing_key='train_status',
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_always_eager=False,
    
    # Monitoring settings
    worker_send_task_events=True,
    task_send_sent_event=True
)

# Export celery app
celery = app 