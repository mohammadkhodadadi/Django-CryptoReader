import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Create a Celery instance
app = Celery('project')

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs
app.autodiscover_tasks()
