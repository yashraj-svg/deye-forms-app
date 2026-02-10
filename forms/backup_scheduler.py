"""
Scheduler setup for automated S3 backups
This runs in your Django app and schedules daily backups
"""

import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

logger = logging.getLogger(__name__)


def start_backup_scheduler():
    """Start the backup scheduler"""
    
    # Only enable in production or if explicitly enabled
    if not os.environ.get('ENABLE_BACKUPS', 'False').lower() == 'true':
        logger.info('Backups disabled (set ENABLE_BACKUPS=true to enable)')
        return
    
    scheduler = BackgroundScheduler()
    
    # Schedule daily backup at 2 AM UTC
    scheduler.add_job(
        run_daily_backup,
        'cron',
        hour=2,
        minute=0,
        id='daily_s3_backup',
        name='Daily S3 Backup',
        replace_existing=True
    )
    
    try:
        scheduler.start()
        logger.info('✅ Backup scheduler started - Daily backups at 02:00 UTC')
    except Exception as e:
        logger.error(f'❌ Failed to start backup scheduler: {e}')


def run_daily_backup():
    """Run the backup command"""
    try:
        logger.info('📦 Running scheduled S3 backup...')
        call_command('backup_to_s3')
        logger.info('✅ S3 backup completed successfully')
    except Exception as e:
        logger.error(f'❌ S3 backup failed: {e}')
