import csv
from django.core.management.base import BaseCommand
from django.db import models
from datetime import datetime
from forms.models import StockItem


class Command(BaseCommand):
    help = 'Load stock items from CSV fixture'

    def handle(self, *args, **options):
        csv_path = 'forms/fixtures/stock_data.csv'
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Batch create for performance
                batch_size = 1000
                batch = []
                count = 0
                
                for row in reader:
                    # Parse shipment_date
                    shipment_date = None
                    if row.get('shipment_date') and row['shipment_date'].strip():
                        try:
                            shipment_date = datetime.fromisoformat(row['shipment_date']).date()
                        except (ValueError, TypeError):
                            shipment_date = None
                    
                    stock_item = StockItem(
                        pcba_sn_old=row.get('pcba_sn_old') or None,
                        pcba_sn_new=row.get('pcba_sn_new', '').strip(),
                        component_type=row.get('component_type') or None,
                        specification=row.get('specification') or None,
                        quantity=float(row.get('quantity', 0)) if row.get('quantity') else 0,
                        remark=row.get('remark') or None,
                        year=int(row.get('year', 2025)) if row.get('year') else 2025,
                        shipment_date=shipment_date,
                    )
                    batch.append(stock_item)
                    count += 1
                    
                    # Batch insert
                    if len(batch) >= batch_size:
                        StockItem.objects.bulk_create(batch, ignore_conflicts=True)
                        self.stdout.write(self.style.SUCCESS(f'✓ Inserted {len(batch)} stock items'))
                        batch = []
                
                # Insert remaining
                if batch:
                    StockItem.objects.bulk_create(batch, ignore_conflicts=True)
                    self.stdout.write(self.style.SUCCESS(f'✓ Inserted {len(batch)} stock items'))
                
                self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully loaded {count} stock items from {csv_path}'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ File not found: {csv_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error loading stock data: {str(e)}'))
