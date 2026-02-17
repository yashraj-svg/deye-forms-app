"""
Django management command to clean up old location tracking records.
Removes location pings older than 4 months (120 days).
Run this command via cron job or scheduled task.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from forms.models import LocationTracking


class Command(BaseCommand):
    help = 'Cleanup location tracking records older than 4 months'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=120,
            help='Delete records older than this many days (default: 120 days / 4 months)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(self.style.NOTICE(f'\n{"="*60}'))
        self.stdout.write(self.style.NOTICE('Location Tracking Data Cleanup'))
        self.stdout.write(self.style.NOTICE(f'{"="*60}\n'))
        
        self.stdout.write(f'Cutoff date: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'Mode: {"DRY RUN" if dry_run else "LIVE DELETE"}\n')
        
        # Get records to be deleted
        old_records = LocationTracking.objects.filter(ping_time__lt=cutoff_date)
        count = old_records.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ No old records found to delete.'))
            return
        
        # Show breakdown by user
        self.stdout.write(f'\nFound {count} records to delete:\n')
        
        # Group by user
        users_summary = old_records.values(
            'user__username', 
            'user__first_name', 
            'user__last_name'
        ).annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        for user in users_summary:
            username = user['user__username']
            full_name = f"{user['user__first_name']} {user['user__last_name']}".strip()
            display_name = full_name if full_name else username
            record_count = user['count']
            self.stdout.write(f'  • {display_name} ({username}): {record_count} records')
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\n⚠ DRY RUN: No records were actually deleted.'))
            self.stdout.write(self.style.NOTICE(f'Run without --dry-run to perform actual deletion.\n'))
        else:
            # Confirm deletion
            self.stdout.write(self.style.WARNING(f'\n⚠ About to delete {count} records permanently!'))
            confirm = input('Type "yes" to confirm deletion: ')
            
            if confirm.lower() == 'yes':
                deleted_count, _ = old_records.delete()
                self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully deleted {deleted_count} old location tracking records.'))
                self.stdout.write(self.style.SUCCESS(f'Storage reclaimed. Data older than {days} days removed.\n'))
            else:
                self.stdout.write(self.style.ERROR('\n✗ Deletion cancelled by user.\n'))


from django.db import models
