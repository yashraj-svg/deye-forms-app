# Auto-generated migration to load stock data fixture

from django.db import migrations


def load_stock_fixture(apps, schema_editor):
    """Load stock items fixture if table is empty"""
    StockItem = apps.get_model('forms', 'StockItem')
    
    # Only load if table is empty
    if StockItem.objects.count() == 0:
        from django.core.management import call_command
        call_command('loaddata', 'stock_items', verbosity=1)


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
