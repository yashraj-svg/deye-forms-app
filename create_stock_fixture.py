"""
Create stock_items.json fixture with proper UTF-8 encoding
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from django.core import serializers
from forms.models import StockItem

print("📦 Creating stock fixture...")

# Get all stock items
stock_items = StockItem.objects.all().order_by('year', 'pcba_sn_new')
count = stock_items.count()

print(f"   Found {count} stock items")

# Serialize to JSON
data = serializers.serialize('json', stock_items, indent=2)

# Write with UTF-8 encoding
output_path = 'forms/fixtures/stock_items.json'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(data)

print(f"✅ Created {output_path}")
print(f"   Size: {os.path.getsize(output_path) / 1024:.1f} KB")
print(f"   Items: {count}")
