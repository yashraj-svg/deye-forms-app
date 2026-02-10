#!/usr/bin/env python
"""
Railway One-Time Script - Run directly on Railway server
This gets uploaded and run as a one-time deployment task
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import StockItem
from django.db import connection
from django.db.models import Sum
from django.core.management import call_command

print("\n🚂 RAILWAY FIX - Cleaning and Reloading Stock")
print("="*60)

# Step 1: Show current state
current_count = StockItem.objects.count()
current_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
print(f"\n1️⃣ Current (WRONG): {current_count} items, {current_qty:.0f} PCS")

# Step 2: Delete all using TRUNCATE
print("\n2️⃣ Deleting ALL stock items...")
with connection.cursor() as cursor:
    cursor.execute('TRUNCATE TABLE forms_stockitem RESTART IDENTITY CASCADE;')
print("   ✅ All deleted")

# Step 3: Load fixture
print("\n3️⃣ Loading correct data from fixture...")
call_command('loaddata', 'stock_items', verbosity=0)
print("   ✅ Data loaded")

# Step 4: Verify
new_count = StockItem.objects.count()
new_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
print(f"\n4️⃣ New (CORRECT): {new_count} items, {new_qty:.0f} PCS")

if new_count == 1976 and abs(new_qty - 259406) < 1:
    print("\n✅✅✅ SUCCESS - Database fixed!")
else:
    print(f"\n⚠️ Warning: Expected 1976 items, got {new_count}")

print("="*60)
