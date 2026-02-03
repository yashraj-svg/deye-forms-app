import os
import csv
from django.core.management.base import BaseCommand
from forms.models import PincodeData


class Command(BaseCommand):
    help = "Load PincodeData from CSV fixture if table is empty."

    def handle(self, *args, **options):
        if PincodeData.objects.exists():
            self.stdout.write(self.style.SUCCESS("PincodeData already populated."))
            return

        fixture_path = os.path.join("forms", "fixtures", "pincode_data.csv")
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR("Fixture not found: forms/fixtures/pincode_data.csv"))
            return

        self.stdout.write("Loading pincodes from CSV...")
        count = 0
        batch = []
        batch_size = 1000
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                batch.append(PincodeData(
                    pincode=row['pincode'],
                    city=row['city'] or None,
                    state=row['state'] or None,
                    global_cargo_region=row['global_cargo_region'] or None,
                    is_oda=None if row['is_oda'] == '' else (row['is_oda'] == '1' or row['is_oda'].lower() == 'true'),
                    deliverable=row['deliverable'] == '1' or row['deliverable'].lower() == 'true',
                    safexpress_is_oda=None if row['safexpress_is_oda'] == '' else (row['safexpress_is_oda'] == '1' or row['safexpress_is_oda'].lower() == 'true'),
                    bluedart_region=row['bluedart_region'] or None,
                ))
                count += 1
                
                if len(batch) >= batch_size:
                    PincodeData.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []
                    self.stdout.write(f"Loaded {count} pincodes...")
        
        if batch:
            PincodeData.objects.bulk_create(batch, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS(f"PincodeData loaded: {count} records."))
