"""
Django management command to backup database to S3 (works with both SQLite and PostgreSQL)
Usage: python manage.py backup_full_database --to-s3
"""

import os
import subprocess
import shutil
import tempfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3


class Command(BaseCommand):
    help = 'Backup entire database to S3 (SQLite or PostgreSQL)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to-s3',
            action='store_true',
            help='Upload to S3 (requires AWS credentials)'
        )
        parser.add_argument(
            '--bucket',
            type=str,
            default=os.environ.get('S3_BUCKET_NAME', 'deye-db-backups'),
            help='S3 bucket name'
        )

    def handle(self, *args, **options):
        db_config = settings.DATABASES['default']
        db_engine = db_config['ENGINE']
        upload_to_s3 = options.get('to_s3', False)
        bucket_name = options['bucket']
        
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            
            if 'sqlite' in db_engine.lower():
                self._backup_sqlite(db_config, timestamp, upload_to_s3, bucket_name)
            elif 'postgresql' in db_engine.lower():
                self._backup_postgresql(db_config, timestamp, upload_to_s3, bucket_name)
            else:
                self.stdout.write(self.style.ERROR(f'❌ Unsupported database: {db_engine}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Backup failed: {str(e)}'))
            import traceback
            traceback.print_exc()

    def _backup_sqlite(self, db_config, timestamp, upload_to_s3, bucket_name):
        """Backup SQLite database"""
        db_path = db_config['NAME']
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'❌ Database file not found: {db_path}'))
            return
        
        backup_filename = f'db_backup_sqlite_{timestamp}.db'
        backup_filepath = os.path.join(tempfile.gettempdir(), backup_filename)
        
        self.stdout.write(self.style.WARNING(f'\n💾 Creating SQLite backup: {backup_filename}'))
        
        try:
            # Copy SQLite database file
            shutil.copy2(db_path, backup_filepath)
            file_size = os.path.getsize(backup_filepath)
            size_mb = file_size / (1024 * 1024)
            
            self.stdout.write(f'   ✅ Database copied successfully ({size_mb:.2f} MB)')
            
            if upload_to_s3:
                self._upload_to_s3(bucket_name, backup_filepath, backup_filename, 'database')
            else:
                self.stdout.write(f'   📍 Local location: {backup_filepath}')
                self.stdout.write('   💡 Use --to-s3 to upload to S3')
            
            self.stdout.write(self.style.SUCCESS('\n✅ SQLITE BACKUP COMPLETE!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
            raise

    def _backup_postgresql(self, db_config, timestamp, upload_to_s3, bucket_name):
        """Backup PostgreSQL database"""
        backup_filename = f'db_backup_postgres_{timestamp}.sql'
        backup_filepath = os.path.join(tempfile.gettempdir(), backup_filename)
        
        self.stdout.write(self.style.WARNING(f'\n💾 Creating PostgreSQL backup: {backup_filename}'))
        
        # Build pg_dump command
        pg_dump_cmd = [
            'pg_dump',
            '--host=' + (db_config.get('HOST') or 'localhost'),
            '--port=' + str(db_config.get('PORT') or 5432),
            '--username=' + db_config.get('USER'),
            '--no-password',
            '--no-owner',
            '--no-privileges',
            '--format=plain',
            db_config['NAME']
        ]
        
        # Set password environment variable for pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config.get('PASSWORD', '')
        
        self.stdout.write(f'   Starting pg_dump...')
        
        try:
            with open(backup_filepath, 'w') as f:
                result = subprocess.run(
                    pg_dump_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )
            
            if result.returncode != 0:
                self.stdout.write(self.style.ERROR(f'   ❌ pg_dump failed: {result.stderr}'))
                return
            
            file_size = os.path.getsize(backup_filepath)
            size_mb = file_size / (1024 * 1024)
            
            self.stdout.write(f'   ✅ Database dumped successfully ({size_mb:.2f} MB)')
            
            if upload_to_s3:
                self._upload_to_s3(bucket_name, backup_filepath, backup_filename, 'database')
            else:
                self.stdout.write(f'   📍 Local location: {backup_filepath}')
                self.stdout.write('   💡 Use --to-s3 to upload to S3')
            
            self.stdout.write(self.style.SUCCESS('\n✅ POSTGRESQL BACKUP COMPLETE!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
            raise

    def _upload_to_s3(self, bucket_name, backup_filepath, backup_filename, backup_type):
        """Upload backup file to S3"""
        # Get AWS credentials from environment
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION', 'ap-south-1')
        
        if not aws_access_key or not aws_secret_key:
            self.stdout.write(self.style.ERROR(
                '   ❌ AWS credentials not found!\n'
                '   Please set: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables'
            ))
            return
        
        try:
            self.stdout.write(f'   Uploading to S3...')
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            
            with open(backup_filepath, 'rb') as f:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=f'{backup_type}-backups/{backup_filename}',
                    Body=f,
                    ContentType='text/plain',
                    ServerSideEncryption='AES256',
                    Metadata={
                        'backup-type': backup_type,
                        'timestamp': datetime.now().isoformat(),
                    }
                )
            
            self.stdout.write(self.style.SUCCESS(f'   ✅ Backup uploaded to S3!'))
            self.stdout.write(f'   📍 Location: s3://{bucket_name}/{backup_type}-backups/{backup_filename}')
            
            # Clean up local backup
            os.remove(backup_filepath)
            self.stdout.write(f'   🧹 Local backup cleaned up')
            
            # Cleanup old backups (keep last 10)
            self.stdout.write(f'\n🧹 Cleaning up old backups (keeping last 10)...')
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=f'{backup_type}-backups/'
            )
            
            if 'Contents' in response:
                objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
                if len(objects) > 10:
                    old_backups = objects[10:]
                    for obj in old_backups:
                        s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                        self.stdout.write(f'   Deleted: {obj["Key"]}')
                    self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {len(old_backups)} old backups'))
                else:
                    self.stdout.write(f'   ✓ All {len(objects)} backups are recent')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ S3 upload failed: {str(e)}'))
            raise
