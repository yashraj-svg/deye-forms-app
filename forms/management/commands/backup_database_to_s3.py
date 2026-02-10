"""
Django management command to backup entire PostgreSQL database to S3
Usage: python manage.py backup_database_to_s3
"""

import os
import subprocess
import json
from datetime import datetime
from django.core.management.base import BaseCommand
import boto3


class Command(BaseCommand):
    help = 'Backup entire PostgreSQL database to S3 as SQL dump'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bucket',
            type=str,
            default=os.environ.get('S3_BUCKET_NAME', 'deye-db-backups'),
            help='S3 bucket name'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['sql', 'custom'],
            default='sql',
            help='Backup format: sql (plain text) or custom (compressed)'
        )

    def handle(self, *args, **options):
        from django.conf import settings
        
        bucket_name = options['bucket']
        backup_format = options['format']
        
        # Get AWS credentials from environment
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION', 'ap-south-1')
        
        if not aws_access_key or not aws_secret_key:
            self.stdout.write(self.style.ERROR(
                '❌ AWS credentials not found!\n'
                '   Please set: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables'
            ))
            return
        
        # Get database connection info
        db_config = settings.DATABASES['default']
        
        if db_config['ENGINE'] != 'django.db.backends.postgresql':
            self.stdout.write(self.style.ERROR(
                '❌ This command only works with PostgreSQL databases!'
            ))
            return
        
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            file_ext = 'sql' if backup_format == 'sql' else 'dump'
            backup_filename = f'db_backup_{timestamp}.{file_ext}'
            backup_filepath = f'/tmp/{backup_filename}'
            
            self.stdout.write(self.style.WARNING(f'\n💾 Creating database backup: {backup_filename}'))
            
            # Build pg_dump command
            pg_dump_cmd = [
                'pg_dump',
                '--host=' + (db_config.get('HOST') or 'localhost'),
                '--port=' + str(db_config.get('PORT') or 5432),
                '--username=' + db_config.get('USER'),
                '--no-password',
                '--no-owner',
                '--no-privileges',
            ]
            
            if backup_format == 'custom':
                pg_dump_cmd.extend(['--format=custom', '--compress=9'])
            else:
                pg_dump_cmd.append('--format=plain')
            
            pg_dump_cmd.append(db_config['NAME'])
            
            # Set password environment variable for pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config.get('PASSWORD', '')
            
            self.stdout.write(f'   Starting pg_dump...')
            
            # Run pg_dump
            with open(backup_filepath, 'w') as f:
                result = subprocess.run(
                    pg_dump_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )
            
            if result.returncode != 0:
                self.stdout.write(self.style.ERROR(
                    f'   ❌ pg_dump failed: {result.stderr}'
                ))
                return
            
            # Get backup file size
            file_size = os.path.getsize(backup_filepath)
            size_mb = file_size / (1024 * 1024)
            
            self.stdout.write(f'   ✅ Database dumped successfully ({size_mb:.2f} MB)')
            
            # Upload to S3
            self.stdout.write(f'   Uploading to S3...')
            
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                
                with open(backup_filepath, 'rb') as f:
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=f'database-backups/{backup_filename}',
                        Body=f,
                        ContentType='text/plain' if backup_format == 'sql' else 'application/octet-stream',
                        ServerSideEncryption='AES256',
                        Metadata={
                            'backup-type': 'full-database',
                            'database': db_config['NAME'],
                            'timestamp': timestamp,
                        }
                    )
                
                self.stdout.write(self.style.SUCCESS(f'   ✅ Backup uploaded to S3!'))
                self.stdout.write(f'   📍 Location: s3://{bucket_name}/database-backups/{backup_filename}')
                self.stdout.write(f'   💾 Size: {size_mb:.2f} MB')
                
                # Clean up local backup
                os.remove(backup_filepath)
                self.stdout.write(f'   🧹 Local backup cleaned up')
                
            except Exception as upload_error:
                self.stdout.write(self.style.ERROR(
                    f'   ❌ S3 upload failed: {str(upload_error)}'
                ))
                # Try to clean up local file anyway
                try:
                    os.remove(backup_filepath)
                except:
                    pass
                return
            
            # Keep only last 10 database backups (they're larger)
            self.stdout.write('\n🧹 Cleaning up old backups (keeping last 10)...')
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix='database-backups/'
                )
                
                if 'Contents' in response:
                    objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
                    
                    if len(objects) > 10:
                        old_backups = objects[10:]  # Keep last 10, delete rest
                        for obj in old_backups:
                            s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                            self.stdout.write(f'   Deleted: {obj["Key"]}')
                        self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {len(old_backups)} old backups'))
                    else:
                        self.stdout.write(f'   ✓ All {len(objects)} backups are recent')
            except Exception as cleanup_error:
                self.stdout.write(f'   ⚠️  Cleanup skipped: {str(cleanup_error)[:100]}')
            
            self.stdout.write(self.style.SUCCESS('\n✅ DATABASE BACKUP COMPLETE!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Backup failed: {str(e)}'))
            import traceback
            traceback.print_exc()
