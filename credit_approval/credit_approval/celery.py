from celery import Celery
import os

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_approval.settings')

app = Celery('credit_approval')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True

# Auto-discover tasks from all registered Django app configs
app.autodiscover_tasks()
