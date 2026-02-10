from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forms'
    
    def ready(self):
        """Start backup scheduler when app is ready"""
        try:
            from .backup_scheduler import start_backup_scheduler
            start_backup_scheduler()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Could not start backup scheduler: {e}')
