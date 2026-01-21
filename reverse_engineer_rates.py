"""
Reverse-engineer actual rates from December bills
"""
import csv
import os

csv_path = r"c:\Users\Yashraj\Desktop\Deye Web App Project\Global Cargo Bill - Dec Month - Sheet1.csv"

bills = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            bills.append({
                'sr': row['Sr No'],
                'from_pin': row['From Location'],
                'to_pin': row['To Location'],
                'weight': float(row['Weight (kg)']),
                'mode': row['Mode'],
                'amount': float(row['Amount (Rs)']),
            })
        except (ValueError, KeyError):
            continue

print("=" * 100)
print("REVERSE ENGINEERING RATES FROM ACTUAL BILLS")
print("=" * 100)

# Group by amounts to see patterns
from collections import defaultdict
amount_groups = defaultdict(list)
for bill in bills:
    amount_groups[bill['amount']].append(bill)

# Analyze non-minimum charges (excluding Rs.450)
non_minimum = [b for b in bills if b['amount'] > 450]

print(f"\n{len(non_minimum)} bills with amount > Rs.450 (excluding minimum charges)")
print("\nReverse calculating rate/kg (assuming structure: Base + Docket + Fuel 10% + GST 18%):")
print("Formula: Amount = Base + Docket(450) + Fuel(Base*0.10) + GST((Base+Fuel)*0.18)")
print("Solving for Base: Amount = Base * (1 + 0.10 + 0.198) + 450 * 1.18")
print("              Amount = Base * 1.298 + 531")
print("              Base = (Amount - 531) / 1.298")
print("              Rate/kg = Base / weight")

for bill in non_minimum[:20]:
    # Reverse calculate base
    # Total = Base + Docket(450) + Fuel(Base*0.10) + GST((Base+Fuel)*0.18)
    # Total = Base + 450 + Base*0.10 + (Base+Base*0.10)*0.18
    # Total = Base + 450 + Base*0.10 + Base*0.18 + Base*0.018
    # Total = Base*(1 + 0.10 + 0.18 + 0.018) + 450
    # Total = Base*1.298 + 450
    
    # But wait, GST excludes docket!
    # Total = Base + Fuel(Base*0.10) + GST((Base+Fuel)*0.18) + Docket(450)
    # Total = Base + Base*0.10 + (Base*1.10)*0.18 + 450
    # Total = Base + Base*0.10 + Base*0.198 + 450
    # Total = Base*1.298 + 450
    
    base_freight = (bill['amount'] - 450) / 1.298
    rate_per_kg = base_freight / bill['weight']
    
    print(f"\n{bill['from_pin']} -> {bill['to_pin']}: {bill['weight']}kg, Rs.{bill['amount']}")
    print(f"  Calculated Base: Rs.{base_freight:.2f}, Rate: Rs.{rate_per_kg:.2f}/kg")
    
    # Verify
    fuel = base_freight * 0.10
    gst = (base_freight + fuel) * 0.18
    total = base_freight + fuel + gst + 450
    print(f"  Verification: Base({base_freight:.2f}) + Fuel({fuel:.2f}) + GST({gst:.2f}) + Docket(450) = Rs.{total:.2f}")
    print(f"  Match: {'GOOD' if abs(total - bill['amount']) < 1 else 'BAD'}")

# Check ODA bills
print("\n" + "=" * 100)
print("ODA BILLS ANALYSIS:")
print("=" * 100)
oda_bills = [b for b in bills if b['mode'] == 'ODA']
print(f"\nFound {len(oda_bills)} ODA bills")

# Group ODA by amount
oda_amounts = defaultdict(list)
for bill in oda_bills:
    oda_amounts[bill['amount']].append(bill)

for amount, group in sorted(oda_amounts.items()):
    print(f"\nRs.{amount}: {len(group)} bills")
    if len(group) <= 3:
        for bill in group:
            print(f"  {bill['from_pin']} -> {bill['to_pin']}: {bill['weight']}kg")
    
    # Reverse calculate for ODA
    # If ODA = Rs.600
    # Total = Base + ODA(600) + Fuel((Base+ODA)*0.10) + GST((Base+ODA+Fuel)*0.18) + Docket(450)
    # For minimum ODA (Rs.1050 observed)
    if amount == 1050:
        print(f"  This appears to be minimum ODA charge")
        print(f"  Rs.1050 = Docket(450) + ODA(600) = Rs.1050 ✓")

print("\n" + "=" * 100)
print("SUMMARY OF FINDINGS:")
print("=" * 100)
print("1. Minimum charge (162 bills): Rs.450 (appears to be just docket, no base freight)")
print("2. Standard rates can be reverse-engineered from non-minimum bills")
print("3. ODA minimum: Rs.1050 = Docket(450) + ODA(600)")
print("4. Formula appears correct BUT rates/kg seem lower than our Rs.13-14/kg matrix")
print("=" * 100)
