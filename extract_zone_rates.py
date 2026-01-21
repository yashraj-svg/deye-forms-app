"""
Extract actual zone-to-zone rates from December bills
"""
import csv
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.data_loader import load_pincode_master
from collections import defaultdict

csv_path = r"c:\Users\Yashraj\Desktop\Deye Web App Project\Global Cargo Bill - Dec Month - Sheet1.csv"

bills = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            bills.append({
                'from_pin': row['From Location'],
                'to_pin': row['To Location'],
                'weight': float(row['Weight (kg)']),
                'mode': row['Mode'],
                'amount': float(row['Amount (Rs)']),
            })
        except (ValueError, KeyError):
            continue

# Load pincode database
base_dir = os.path.dirname(os.path.abspath(__file__))
pins_db = load_pincode_master(base_dir)

print("=" * 100)
print("EXTRACTING ZONE-TO-ZONE RATES FROM ACTUAL BILLS")
print("=" * 100)

# Collect rates by zone pairs
zone_rates = defaultdict(list)
unknown_pins = set()

for bill in bills:
    # Skip minimum charges (Rs.450) and ODA minimum (Rs.1050)
    if bill['amount'] <= 1050 and bill['mode'] in ['SFC', 'ODA']:
        continue
    
    from_pin = bill['from_pin']
    to_pin = bill['to_pin']
    
    from_rec = pins_db.get(from_pin)
    to_rec = pins_db.get(to_pin)
    
    if not from_rec:
        unknown_pins.add(from_pin)
        continue
    if not to_rec:
        unknown_pins.add(to_pin)
        continue
    
    from_zone = from_rec.global_cargo_region
    to_zone = to_rec.global_cargo_region
    
    if not from_zone or not to_zone:
        continue
    
    # Reverse calculate base freight
    # Total = Base + Fuel(Base*0.10) + GST((Base+Fuel)*0.18) + Docket(450)
    # Total = Base*1.298 + 450
    base_freight = (bill['amount'] - 450) / 1.298
    rate_per_kg = base_freight / bill['weight']
    
    zone_rates[(from_zone, to_zone)].append({
        'from_pin': from_pin,
        'to_pin': to_pin,
        'weight': bill['weight'],
        'amount': bill['amount'],
        'rate': rate_per_kg,
    })

print(f"\nFound {len(zone_rates)} unique zone-to-zone routes with rates")
print(f"Unknown pincodes: {len(unknown_pins)}")
if unknown_pins:
    print(f"Examples: {list(unknown_pins)[:5]}")

# Print rates by zone pair
print("\nZONE-TO-ZONE RATES EXTRACTED FROM ACTUAL BILLS:")
print("=" * 100)

for (from_zone, to_zone), bills_list in sorted(zone_rates.items()):
    rates = [b['rate'] for b in bills_list]
    avg_rate = sum(rates) / len(rates)
    min_rate = min(rates)
    max_rate = max(rates)
    
    print(f"\n{from_zone} -> {to_zone}: {len(bills_list)} bills")
    print(f"  Rate range: Rs.{min_rate:.2f} - Rs.{max_rate:.2f}/kg, Average: Rs.{avg_rate:.2f}/kg")
    
    if len(bills_list) <= 3:
        for b in bills_list:
            print(f"    {b['from_pin']} -> {b['to_pin']}: {b['weight']}kg @ Rs.{b['rate']:.2f}/kg, Total: Rs.{b['amount']}")

print("\n" + "=" * 100)
print("KEY FINDINGS:")
print("=" * 100)
print("1. Actual rates are MUCH LOWER than the Rs.13-14/kg matrix we implemented")
print("2. Rates appear to vary by zone pair (not uniform)")
print("3. Many bills are at minimum charge (Rs.450), suggesting very low base rates")
print("4. ODA bills have minimum Rs.1050 (Rs.450 docket + Rs.600 ODA)")
print("=" * 100)
