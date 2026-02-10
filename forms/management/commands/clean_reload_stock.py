"""
Django management command to clean and reload stock data
This DELETES ALL stock items and reloads from fixture
"""

from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.core.management import call_command
from forms.models import StockItem
from django.db.models import Sum


class Command(BaseCommand):
    help = 'Clean all stock items and reload from fixture (for Railway PostgreSQL)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of ALL stock items',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.ERROR(
                '\n⚠️  WARNING: This will DELETE ALL stock items and reload from fixture!\n'
                'Run with --confirm flag to proceed:\n'
                'python manage.py clean_reload_stock --confirm\n'
            ))
            return

        self.stdout.write(self.style.WARNING('\n' + '='*70))
        self.stdout.write(self.style.WARNING('🧹 CLEANING AND RELOADING STOCK DATA'))
        self.stdout.write(self.style.WARNING('='*70))

        # Step 1: Show current state
        self.stdout.write('\n📊 STEP 1: Current database state...')
        current_count = StockItem.objects.count()
        current_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
        self.stdout.write(f'   Items: {current_count}')
        self.stdout.write(f'   Quantity: {current_qty:.0f} PCS')

        # Step 2: TRUNCATE table (fastest, most thorough)
        self.stdout.write('\n🗑️  STEP 2: Truncating stock_items table...')
        try:
            with connection.cursor() as cursor:
                # Use TRUNCATE for PostgreSQL (faster than DELETE)
                table_name = StockItem._meta.db_table
                cursor.execute(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;')
            self.stdout.write(self.style.SUCCESS(f'   ✅ Table {table_name} truncated'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   TRUNCATE failed: {e}'))
            self.stdout.write('   Falling back to DELETE...')
            # Fallback to DELETE ALL
            deleted_count, _ = StockItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {deleted_count} items'))

        # Verify deletion
        remaining = StockItem.objects.count()
        if remaining == 0:
            self.stdout.write(self.style.SUCCESS('   ✅ Database cleared successfully'))
        else:
            self.stdout.write(self.style.ERROR(f'   ❌ Warning: {remaining} items still remain!'))
            return

        # Step 3: Load fixture
        self.stdout.write('\n📥 STEP 3: Loading stock data from fixture...')
        try:
            call_command('loaddata', 'stock_items', verbosity=0)
            self.stdout.write(self.style.SUCCESS('   ✅ Fixture loaded'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error loading fixture: {e}'))
            return

        # Step 4: Verify new data
        self.stdout.write('\n✅ STEP 4: Verifying reloaded data...')
        new_count = StockItem.objects.count()
        new_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0

        self.stdout.write(f'   Items: {new_count}')
        self.stdout.write(f'   Quantity: {new_qty:.0f} PCS')

        # Step 5: Validation
        expected_items = 1976
        expected_qty = 259406

        self.stdout.write('\n🔍 STEP 5: Validation...')
        if new_count == expected_items and abs(new_qty - expected_qty) < 1:
            self.stdout.write(self.style.SUCCESS(f'   ✅ PERFECT MATCH!'))
            self.stdout.write(self.style.SUCCESS(f'      Items: {new_count} ✓'))
            self.stdout.write(self.style.SUCCESS(f'      Quantity: {new_qty:.0f} PCS ✓'))
        else:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Data differs from expected:'))
            self.stdout.write(f'      Expected: {expected_items} items, {expected_qty} PCS')
            self.stdout.write(f'      Got: {new_count} items, {new_qty:.0f} PCS')
            if new_count != expected_items:
                self.stdout.write(f'      Difference: {new_count - expected_items} items')
            if abs(new_qty - expected_qty) > 1:
                self.stdout.write(f'      Difference: {new_qty - expected_qty:.0f} PCS')

        # Step 6: Show breakdown
        self.stdout.write('\n📋 STEP 6: Data breakdown by year...')
        year_breakdown = StockItem.objects.values('year').annotate(
            count=models.Count('id'),
            qty=Sum('quantity')
        ).order_by('year')

        for year_data in year_breakdown:
            self.stdout.write(f'      {year_data["year"]}: {year_data["count"]} items = {year_data["qty"]:.0f} PCS')

        # Final message
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ DATABASE CLEANED AND RELOADED SUCCESSFULLY!'))
        self.stdout.write('='*70)
        self.stdout.write('\n📝 Next steps:')
        self.stdout.write('   1. Restart your web application')
        self.stdout.write('   2. Clear browser cache (Ctrl+Shift+Delete)')
        self.stdout.write('   3. Visit: /stock/received/')
        self.stdout.write('   4. Verify: Should show 1,085 merged items, 259,406 PCS\n')


from django.db import models
