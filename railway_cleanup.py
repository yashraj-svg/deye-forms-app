#!/usr/bin/env python
"""
Railway Database Cleanup and Reload Script
Clears old stock data and reloads from fixture
"""

import os
import sys
import django
from pathlib import Path

def cleanup_and_reload():
    """Clean up Railway database and reload stock data"""
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
    django.setup()
    
    from forms.models import StockItem
    from django.db.models import Sum
    from django.core.management import call_command
    
    print("\n" + "="*70)
    print("🚀 RAILWAY DATABASE CLEANUP & RELOAD")
    print("="*70)
    
    # Step 1: Check current state
    print("\n📊 STEP 1: Checking current database state...")
    current_count = StockItem.objects.count()
    current_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    print(f"   Current items: {current_count}")
    print(f"   Current quantity: {current_qty:.0f} PCS")
    
    # Step 2: Backup info (optional)
    print("\n💾 STEP 2: Getting item details before cleanup...")
    total_by_year = StockItem.objects.values('year').annotate(
        count=django.db.models.Count('id'),
        qty=Sum('quantity')
    ).order_by('year')
    
    print("   Items by year (before):")
    for year_data in total_by_year:
        print(f"      {year_data['year']}: {year_data['count']} items = {year_data['qty']:.0f} PCS")
    
    # Step 3: Clear old data
    print("\n🗑️  STEP 3: Deleting all stock items from database...")
    deleted_count, _ = StockItem.objects.all().delete()
    print(f"   ✅ Deleted {deleted_count} items")
    
    # Verify deletion
    remaining = StockItem.objects.count()
    if remaining == 0:
        print("   ✅ Database cleared successfully")
    else:
        print(f"   ⚠️  Warning: {remaining} items still remain!")
        return False
    
    # Step 4: Load fixture
    print("\n📥 STEP 4: Loading stock data from fixture...")
    try:
        call_command('loaddata', 'stock_items', verbosity=1)
        print("   ✅ Fixture loaded")
    except Exception as e:
        print(f"   ❌ Error loading fixture: {e}")
        print("   Trying alternative method...")
        try:
            call_command('loaddata', 'stock_items')
            print("   ✅ Fixture loaded (alternative)")
        except Exception as e2:
            print(f"   ❌ Failed: {e2}")
            return False
    
    # Step 5: Verify new data
    print("\n✅ STEP 5: Verifying reloaded data...")
    new_count = StockItem.objects.count()
    new_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    print(f"   New items: {new_count}")
    print(f"   New quantity: {new_qty:.0f} PCS")
    
    # Step 6: Final validation
    print("\n🔍 STEP 6: Validation...")
    expected_items = 1976
    expected_qty = 259406
    
    if new_count == expected_items and abs(new_qty - expected_qty) < 1:
        print(f"   ✅ PERFECT MATCH!")
        print(f"      Items: {new_count} ✓")
        print(f"      Quantity: {new_qty:.0f} PCS ✓")
    else:
        print(f"   ⚠️  Data doesn't match expected values:")
        print(f"      Expected: {expected_items} items, {expected_qty} PCS")
        print(f"      Got: {new_count} items, {new_qty:.0f} PCS")
        if new_count != expected_items or abs(new_qty - expected_qty) > 1:
            print(f"      Difference: {new_count - expected_items} items, {new_qty - expected_qty:.0f} PCS")
    
    # Step 7: Show breakdown
    print("\n📋 STEP 7: Data breakdown by year...")
    final_by_year = StockItem.objects.values('year').annotate(
        count=django.db.models.Count('id'),
        qty=Sum('quantity')
    ).order_by('year')
    
    for year_data in final_by_year:
        print(f"      {year_data['year']}: {year_data['count']} items = {year_data['qty']:.0f} PCS")
    
    print("\n" + "="*70)
    print("✅ DATABASE CLEANUP & RELOAD COMPLETE!")
    print("="*70)
    print("\n📝 Next steps:")
    print("   1. Restart Railway application")
    print("   2. Visit: https://deycindia.in/stock/received/")
    print("   3. Verify: Total Items should be 1,085")
    print("   4. Verify: Total Quantity should be 259,406 PCS")
    print("\n")
    
    return True


if __name__ == '__main__':
    try:
        success = cleanup_and_reload()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
