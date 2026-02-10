"""
Export StockItem fixture with proper UTF-8 encoding
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import StockItem
from django.core import serializers
import sys

print('📦 Creating stock data fixture...')

# Get all StockItems
items = StockItem.objects.all()
total = items.count()

# Serialize to JSON with UTF-8 encoding
fixture_data = serializers.serialize('json', items, indent=2, ensure_ascii=False)

# Write to file with UTF-8 encoding
output_path = 'forms/fixtures/stock_items.json'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(fixture_data)

print(f'✅ Fixture created successfully!')
print(f'   File: {output_path}')
print(f'   Items: {total}')
print(f'   Size: {os.path.getsize(output_path) / 1024:.1f} KB')

print(f'\n📖 To load this fixture on another machine:')
print(f'   python manage.py loaddata stock_items')
