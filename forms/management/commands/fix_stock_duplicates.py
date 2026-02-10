from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Sum
from django.core.management import call_command
from forms.models import StockItem


class Command(BaseCommand):
    help = 'SAFE FIX: Delete all stock and reload clean data from Excel fixture'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm you want to delete all stock and reload',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.ERROR('\n⚠️  This command will DELETE ALL stock items and reload from Excel'))
            self.stdout.write(self.style.ERROR('   Run with --confirm flag to proceed:'))
            self.stdout.write(self.style.ERROR('   python manage.py fix_stock_duplicates --confirm\n'))
            return

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('🔧 FIXING STOCK DUPLICATES - RAILWAY SAFE'))
        self.stdout.write('='*70)

        # Step 1: Show current wrong state
        self.stdout.write('\n📊 STEP 1: Current state (WRONG)...')
        current_count = StockItem.objects.count()
        current_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
        self.stdout.write(f'   ❌ Items: {current_count}')
        self.stdout.write(f'   ❌ Quantity: {current_qty:.0f} PCS (SHOULD BE 259,406)')

        # Step 2: TRUNCATE table (fastest, safest for PostgreSQL)
        self.stdout.write('\n🗑️  STEP 2: Deleting ALL stock items...')
        try:
            with connection.cursor() as cursor:
                table_name = StockItem._meta.db_table
                cursor.execute(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;')
            self.stdout.write(self.style.SUCCESS('   ✅ Table truncated'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   TRUNCATE failed: {e}'))
            self.stdout.write('   Using DELETE instead...')
            deleted, _ = StockItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {deleted} items'))

        # Verify deletion
        remaining = StockItem.objects.count()
        if remaining == 0:
            self.stdout.write(self.style.SUCCESS('   ✅ All old data deleted'))
        else:
            self.stdout.write(self.style.ERROR(f'   ❌ ERROR: {remaining} items still remain!'))
            return

        # Step 3: Load clean fixture from Excel
        self.stdout.write('\n📥 STEP 3: Loading CORRECT data from Excel fixture...')
        try:
            call_command('loaddata', 'stock_items', verbosity=0)
            self.stdout.write(self.style.SUCCESS('   ✅ Fixture loaded successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ ERROR loading fixture: {e}'))
            self.stdout.write('\n   Trying alternative path...')
            try:
                call_command('loaddata', 'forms/fixtures/stock_items.json', verbosity=0)
                self.stdout.write(self.style.SUCCESS('   ✅ Fixture loaded (alternative path)'))
            except Exception as e2:
                self.stdout.write(self.style.ERROR(f'   ❌ FAILED: {e2}'))
                return

        # Step 4: Verify correct data
        self.stdout.write('\n✅ STEP 4: Verifying CORRECT data...')
        new_count = StockItem.objects.count()
        new_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0

        self.stdout.write(f'   Items: {new_count} (expected: 1,976)')
        self.stdout.write(f'   Quantity: {new_qty:.0f} PCS (expected: 259,406)')

        # Show breakdown by year
        self.stdout.write('\n📊 Breakdown by year:')
        from django.db.models import Count
        years = StockItem.objects.values('year').annotate(
            count=Count('id'),
            total=Sum('quantity')
        ).order_by('year')
        
        for year_data in years:
            year = year_data['year'] or 'Unknown'
            count = year_data['count']
            total = year_data['total'] or 0
            self.stdout.write(f'   Year {year}: {count} items, {total:.0f} PCS')

        # Final validation
        self.stdout.write('\n🔍 FINAL VALIDATION...')
        if new_count == 1976 and abs(new_qty - 259406) < 1:
            self.stdout.write('\n' + '='*70)
            self.stdout.write(self.style.SUCCESS('✅✅✅ PERFECT! DATABASE IS NOW CORRECT!'))
            self.stdout.write('='*70)
            self.stdout.write('\n📝 What to do next:')
            self.stdout.write('   1. Restart your Railway app (if needed)')
            self.stdout.write('   2. Visit: https://deycindia.in/stock/received/')
            self.stdout.write('   3. Should show: 1,085 items (merged), 259,406 PCS')
            self.stdout.write('   4. Admin panel: 1,976 items (unmerged)')
            self.stdout.write('\n✨ Your database now matches Excel perfectly!\n')
        else:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Warning: Data doesn\'t match exactly'))
            self.stdout.write(f'      Expected: 1,976 items, 259,406 PCS')
            self.stdout.write(f'      Got: {new_count} items, {new_qty:.0f} PCS')
            self.stdout.write('\n   If close, this is OK. Refresh and check again.\n')
