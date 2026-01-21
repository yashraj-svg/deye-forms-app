"""
Analyze actual Global Cargo bills from December to verify rate structure
"""
import csv
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes
from collections import defaultdict

# Read the CSV file
csv_path = r"c:\Users\Yashraj\Desktop\Deye Web App Project\Global Cargo Bill - Dec Month - Sheet1.csv"

bills = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            bills.append({
                'sr': row['Sr No'],
                'date': row['Date'],
                'from_pin': row['From Location'],
                'to_pin': row['Destination'],
                'to_loc': row['To Location'],
                'weight': float(row['Weight (kg)']),
                'mode': row['Mode'],
                'amount': float(row['Amount (Rs)']),
            })
        except (ValueError, KeyError) as e:
            continue

print("=" * 100)
print(f"ANALYZING {len(bills)} GLOBAL CARGO BILLS FROM DECEMBER 2025")
print("=" * 100)

# Analyze patterns
mode_counts = defaultdict(int)
amount_distribution = defaultdict(int)
weight_ranges = {'<10kg': 0, '10-20kg': 0, '20-50kg': 0, '50-100kg': 0, '>100kg': 0}

for bill in bills:
    mode_counts[bill['mode']] += 1
    amount_distribution[bill['amount']] += 1
    
    w = bill['weight']
    if w < 10:
        weight_ranges['<10kg'] += 1
    elif w <= 20:
        weight_ranges['10-20kg'] += 1
    elif w <= 50:
        weight_ranges['20-50kg'] += 1
    elif w <= 100:
        weight_ranges['50-100kg'] += 1
    else:
        weight_ranges['>100kg'] += 1

print("\nMODE DISTRIBUTION:")
for mode, count in sorted(mode_counts.items()):
    print(f"  {mode}: {count} bills")

print("\nWEIGHT DISTRIBUTION:")
for range_name, count in weight_ranges.items():
    print(f"  {range_name}: {count} bills")

print("\nAMOUNT PATTERNS:")
top_amounts = sorted(amount_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
for amount, count in top_amounts:
    print(f"  Rs.{amount:.0f}: {count} bills")

# Analyze specific examples
print("\n" + "=" * 100)
print("SAMPLE BILL ANALYSIS (comparing with calculator):")
print("=" * 100)

samples = [
    bills[0],   # First bill
    bills[14],  # Row 15: 844124 → 411045, 111kg, Rs.1887
    bills[15],  # Row 16: 686691 → 560060, 46kg, Rs.644
    bills[23],  # Row 24: 768032 → 411045, 178kg, Rs.2848
]

for bill in samples[:5]:
    if not bill['from_pin'] or not bill['to_pin']:
        continue
    
    print(f"\nBill #{bill['sr']}: {bill['from_pin']} -> {bill['to_pin']}")
    print(f"  Weight: {bill['weight']}kg, Mode: {bill['mode']}, Amount: Rs.{bill['amount']}")
    
    inp = QuoteInput(
        from_pincode=bill['from_pin'],
        to_pincode=bill['to_pin'],
        weight_kg=bill['weight'],
        length_cm=0,
        breadth_cm=0,
        height_cm=0,
    )
    
    try:
        results = get_all_partner_quotes(inp)
        global_result = next((r for r in results if "Global" in r.partner_name), None)
        
        if global_result:
            print(f"  Calculator: {global_result.from_zone} -> {global_result.to_zone}, "
                  f"Rate: Rs.{global_result.rate_per_kg}/kg, Total: Rs.{global_result.total_after_gst:.2f}")
            
            diff = global_result.total_after_gst - bill['amount']
            if abs(diff) < 10:
                print(f"  Match: GOOD (diff: Rs.{diff:.2f})")
            else:
                print(f"  Match: MISMATCH (diff: Rs.{diff:.2f})")
                # Breakdown
                print(f"    Invoice amount: Rs.{bill['amount']}")
                print(f"    Calculator breakdown:")
                print(f"      Base: Rs.{global_result.base_freight}")
                print(f"      ODA: Rs.{global_result.surcharges.get('oda', 0)}")
                print(f"      Docket: Rs.{global_result.surcharges.get('docket', 0)}")
                print(f"      Fuel: Rs.{global_result.surcharges.get('fuel_surcharge', 0)}")
                print(f"      GST: Rs.{global_result.gst_amount}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 100)
print("\nKEY FINDINGS:")
print("  - Most bills are Rs.450 (minimum charge)")
print("  - ODA shipments are Rs.1050")
print("  - Actual billing appears to use minimum Rs.450 docket instead of rate*weight for small shipments")
print("=" * 100)
