from celery import Celery

from app.core.config import settings


celery_app = Celery("leadhunter", broker=str(settings.redis_url), backend=str(settings.redis_url))
