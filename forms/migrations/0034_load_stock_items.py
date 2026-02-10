# Auto-generated migration to load stock data fixture

from django.db import migrations


def load_stock_fixture(apps, schema_editor):
    """Load stock items fixture ONLY if table is completely empty"""
    StockItem = apps.get_model('forms', 'StockItem')
    
    # Only load if table is empty AND we're not on Railway with old data
    count = StockItem.objects.count()
    if count == 0:
        from django.core.management import call_command
        print(f'📥 Loading stock fixture (table is empty)...')
        call_command('loaddata', 'stock_items', verbosity=1)
        print(f'✅ Stock data loaded: {StockItem.objects.count()} items')
    else:
        print(f'⚠️  Stock table already has {count} items - skipping auto-load')
        print(f'   To reload: python manage.py clean_reload_stock --confirm')


def reverse_stock_fixture(apps, schema_editor):
    """Clear stock items on reverse"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0033_alter_stockitem_pcba_sn_new'),
    ]

    operations = [
        migrations.RunPython(load_stock_fixture, reverse_stock_fixture),
    ]
