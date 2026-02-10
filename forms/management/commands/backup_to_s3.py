"""
Django management command to backup StockItem data to S3
Usage: python manage.py backup_to_s3
"""

import os
import json
import boto3
from datetime import datetime
from django.core import serializers
from django.core.management.base import BaseCommand
from django.db.models import Sum
from forms.models import StockItem


class Command(BaseCommand):
    help = 'Backup StockItem data to S3 as JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bucket',
            type=str,
            default=os.environ.get('S3_BUCKET_NAME', 'deye-db-backups'),
            help='S3 bucket name'
        )

    def handle(self, *args, **options):
        bucket_name = options['bucket']
        
        # Get AWS credentials from environment
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        
        if not aws_access_key or not aws_secret_key:
            self.stdout.write(self.style.ERROR(
                '❌ AWS credentials not found!\n'
                '   Please set: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables'
            ))
            return
        
        try:
            # Create S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            backup_filename = f'stock_backup_{timestamp}.json'
            
            self.stdout.write(self.style.WARNING(f'\n📦 Creating backup: {backup_filename}'))
            
            # Get all stock items
            stock_items = StockItem.objects.all().order_by('year', 'pcba_sn_new')
            count = stock_items.count()
            total_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
            
            self.stdout.write(f'   Found {count} items, {total_qty:.0f} PCS')
            
            # Serialize to JSON
            data = serializers.serialize('json', stock_items, indent=2)
            
            # Add metadata
            backup_data = {
                'metadata': {
                    'timestamp': timestamp,
                    'item_count': count,
                    'total_quantity': float(total_qty),
                    'created_at': datetime.now().isoformat(),
                },
                'data': json.loads(data)
            }
            
            # Convert to JSON string
            backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
            
            # Upload to S3
            self.stdout.write(f'   Uploading to S3...')
            s3_client.put_object(
                Bucket=bucket_name,
                Key=f'daily-backups/{backup_filename}',
                Body=backup_json.encode('utf-8'),
                ContentType='application/json',
                ServerSideEncryption='AES256'
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Backup uploaded successfully!'))
            self.stdout.write(f'   S3 Location: s3://{bucket_name}/daily-backups/{backup_filename}')
            
            # Keep only last 30 backups (optional cleanup)
            self.stdout.write('\n🧹 Cleaning up old backups (keeping last 30)...')
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix='daily-backups/'
                )
                
                if 'Contents' in response:
                    objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
                    
                    if len(objects) > 30:
                        old_backups = objects[30:]  # Keep last 30, delete rest
                        for obj in old_backups:
                            s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                            self.stdout.write(f'   Deleted: {obj["Key"]}')
                        self.stdout.write(self.style.SUCCESS(f'✅ Deleted {len(old_backups)} old backups'))
                    else:
                        self.stdout.write(f'   ✓ All {len(objects)} backups are recent')
            except Exception as cleanup_error:
                self.stdout.write(f'   ⚠️  Cleanup skipped: {str(cleanup_error)[:100]}')
            
            self.stdout.write(self.style.SUCCESS('\n✅ BACKUP COMPLETE!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Backup failed: {str(e)}'))
            import traceback
            traceback.print_exc()
