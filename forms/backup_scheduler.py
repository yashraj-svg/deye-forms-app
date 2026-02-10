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
    
    # Schedule daily stock backup at 2 AM UTC
    scheduler.add_job(
        run_daily_backup,
        'cron',
        hour=2,
        minute=0,
        id='daily_s3_backup',
        name='Daily Stock Backup',
        replace_existing=True
    )
    
    # Schedule database backup at 3 AM UTC (1 hour after stock backup)
    scheduler.add_job(
        run_database_backup,
        'cron',
        hour=3,
        minute=0,
        id='daily_db_backup',
        name='Daily Database Backup',
        replace_existing=True
    )
    
    try:
        scheduler.start()
        logger.info('✅ Backup scheduler started')
        logger.info('   - Stock backup: Daily at 02:00 UTC')
        logger.info('   - Database backup: Daily at 03:00 UTC')
    except Exception as e:
        logger.error(f'❌ Failed to start backup scheduler: {e}')


def run_daily_backup():
    """Run the stock backup command"""
    try:
        logger.info('📦 Running scheduled stock backup...')
        call_command('backup_to_s3')
        logger.info('✅ Stock backup completed successfully')
    except Exception as e:
        logger.error(f'❌ Stock backup failed: {e}')


def run_database_backup():
    """Run the database backup command"""
    try:
        logger.info('💾 Running scheduled database backup...')
        call_command('backup_full_database', '--to-s3')
        logger.info('✅ Database backup completed successfully')
    except Exception as e:
        logger.error(f'❌ Database backup failed: {e}')
