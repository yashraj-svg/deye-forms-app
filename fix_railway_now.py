#!/usr/bin/env python
"""
SIMPLE RAILWAY FIX - Run this on Railway to fix the database
This will DELETE all old stock and reload correct data
"""

import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')

import django
django.setup()

from forms.models import StockItem
from django.db.models import Sum
from django.core.management import call_command
from django.db import connection

print("\n" + "="*70)
print("🚂 RAILWAY DATABASE FIX - DELETE OLD DATA & RELOAD CORRECT DATA")
print("="*70)

# Step 1: Show current state
print("\n📊 STEP 1: Current state (WRONG DATA)...")
current_count = StockItem.objects.count()
current_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
print(f"   ❌ Items: {current_count}")
print(f"   ❌ Quantity: {current_qty:.0f} PCS (SHOULD BE 259,406)")

# Step 2: DELETE EVERYTHING
print("\n🗑️  STEP 2: Deleting ALL old stock items...")
try:
    # Use TRUNCATE for PostgreSQL (fastest)
    with connection.cursor() as cursor:
        table_name = StockItem._meta.db_table
        print(f"   Truncating table: {table_name}")
        cursor.execute(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;')
    print("   ✅ Table truncated")
except Exception as e:
    print(f"   TRUNCATE failed, using DELETE: {e}")
    deleted, _ = StockItem.objects.all().delete()
    print(f"   ✅ Deleted {deleted} items")

# Verify deletion
remaining = StockItem.objects.count()
if remaining == 0:
    print("   ✅ All old data deleted")
else:
    print(f"   ❌ ERROR: {remaining} items still remain!")
    sys.exit(1)

# Step 3: Load correct data
print("\n📥 STEP 3: Loading CORRECT data from fixture...")
try:
    call_command('loaddata', 'stock_items', verbosity=0)
    print("   ✅ Fixture loaded successfully")
except Exception as e:
    print(f"   ❌ ERROR loading fixture: {e}")
    print("\n   Trying alternative method...")
    try:
        call_command('loaddata', 'forms/fixtures/stock_items.json', verbosity=0)
        print("   ✅ Fixture loaded (alternative path)")
    except Exception as e2:
        print(f"   ❌ FAILED: {e2}")
        sys.exit(1)

# Step 4: Verify correct data
print("\n✅ STEP 4: Verifying CORRECT data...")
new_count = StockItem.objects.count()
new_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0

print(f"   ✅ Items: {new_count} (expected: 1,976)")
print(f"   ✅ Quantity: {new_qty:.0f} PCS (expected: 259,406)")

# Final check
print("\n🔍 FINAL VALIDATION...")
if new_count == 1976 and abs(new_qty - 259406) < 1:
    print("   ✅✅✅ PERFECT! Database is now CORRECT!")
    print("\n" + "="*70)
    print("✅ SUCCESS - RAILWAY DATABASE FIXED!")
    print("="*70)
    print("\n📝 What to do next:")
    print("   1. Restart your Railway app (click Restart in dashboard)")
    print("   2. Wait 30 seconds for restart")
    print("   3. Visit: https://deycindia.in/stock/received/")
    print("   4. Should show: 1,085 items, 259,406 PCS")
    print("   5. Clear browser cache (Ctrl+Shift+Delete)")
    print("\n✨ Your database now matches Excel and local machine!")
    print("")
else:
    print(f"   ⚠️  WARNING: Data doesn't match exactly")
    print(f"      Got: {new_count} items, {new_qty:.0f} PCS")
    print(f"      Expected: 1,976 items, 259,406 PCS")
    print("\n   Fix: Run 'python manage.py load_akshay_stock --clear'")

sys.exit(0)
