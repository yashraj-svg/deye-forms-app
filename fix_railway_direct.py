"""
Direct PostgreSQL fix for Railway - No Django needed!
This connects directly to your Railway PostgreSQL database and fixes it.

Run from your local computer:
    cmd /c railway run python fix_railway_direct.py

Railway will automatically provide the DATABASE_URL.
"""

import psycopg
import json
import os

print("\n" + "="*70)
print("🚂 RAILWAY DATABASE DIRECT FIX")
print("="*70)

# Step 1: Get DATABASE_URL from environment
print("\n1️⃣ Getting Railway database URL...")
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL not found in environment!")
    print("\n⚠️  You must run this script using Railway CLI:")
    print("   cmd /c railway run python fix_railway_direct.py")
    print("\nThis ensures Railway automatically provides the DATABASE_URL.")
    exit(1)

print(f"✅ Found database: {database_url[:30]}...")

# Step 2: Connect to database
print("\n2️⃣ Connecting to Railway PostgreSQL...")
try:
    conn = psycopg.connect(database_url)
    cursor = conn.cursor()
    print("✅ Connected!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Step 3: Check current state
print("\n3️⃣ Current state (WRONG)...")
cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantity), 0) FROM forms_stockitem")
current_count, current_qty = cursor.fetchone()
print(f"   Items: {current_count}")
print(f"   Quantity: {current_qty:.0f} PCS")

# Step 4: Delete all stock
print("\n4️⃣ Deleting ALL stock items...")
response = input("   Type 'YES' to confirm deletion: ")
if response != 'YES':
    print("❌ Cancelled")
    exit(0)

cursor.execute("TRUNCATE TABLE forms_stockitem RESTART IDENTITY CASCADE")
conn.commit()
print("✅ All stock deleted")

# Step 5: Load fixture
print("\n5️⃣ Loading fixture from stock_items.json...")
print("   Reading fixture file...")

try:
    with open('forms/fixtures/stock_items.json', 'r', encoding='utf-8') as f:
        fixture_data = json.load(f)
    
    print(f"   Found {len(fixture_data)} items in fixture")
    
    # Insert each item
    inserted = 0
    for item in fixture_data:
        fields = item['fields']
        cursor.execute("""
            INSERT INTO forms_stockitem 
            (pcba_sn_new, pcba_sn_old, component_type, specification, quantity, year, shipment_date, remark, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            fields.get('pcba_sn_new'),
            fields.get('pcba_sn_old'),
            fields.get('component_type'),
            fields.get('specification'),
            fields.get('quantity'),
            fields.get('year'),
            fields.get('shipment_date'),
            fields.get('remark'),
            fields.get('created_at'),
            fields.get('updated_at')
        ))
        inserted += 1
        if inserted % 100 == 0:
            print(f"   Inserted {inserted}/{len(fixture_data)} items...")
    
    conn.commit()
    print(f"✅ Inserted {inserted} items")
    
except FileNotFoundError:
    print("❌ Fixture file not found!")
    print("   Make sure you're running from project root: c:\\Users\\Yashraj\\Desktop\\Deye Web App Project")
    cursor.close()
    conn.close()
    exit(1)
except Exception as e:
    print(f"❌ Error loading fixture: {e}")
    conn.rollback()
    cursor.close()
    conn.close()
    exit(1)

# Step 6: Verify
print("\n6️⃣ Verifying data...")
cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantity), 0) FROM forms_stockitem")
new_count, new_qty = cursor.fetchone()
print(f"   Items: {new_count}")
print(f"   Quantity: {new_qty:.0f} PCS")

if new_count == 1976 and abs(new_qty - 259406) < 1:
    print("\n" + "="*70)
    print("✅✅✅ SUCCESS - DATABASE FIXED!")
    print("="*70)
    print("\n📝 WHAT TO DO NOW:")
    print("   1. Restart your Railway app")
    print("   2. Visit: https://deycindia.in/stock/received/")
    print("   3. Should show: 259,406 PCS")
    print("\n✨ Done!")
else:
    print(f"\n⚠️  Warning: Data doesn't match exactly")
    print(f"   Expected: 1976 items, 259406 PCS")
    print(f"   Got: {new_count} items, {new_qty:.0f} PCS")

cursor.close()
conn.close()
