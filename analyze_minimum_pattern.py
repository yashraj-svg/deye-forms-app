"""
Deep analysis of December billing pattern
"""
import csv

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
print("DECEMBER BILLING PATTERN ANALYSIS")
print("=" * 100)

# Key observation: Bill #13 charged Rs.180 for 2.3kg (way below Rs.450 minimum)
# This suggests NO minimum LR of Rs.450 in December!

print("\nBills BELOW Rs.450:")
below_450 = [b for b in bills if b['amount'] < 450 and b['from_pin'] != '#N/A']
print(f"Found {len(below_450)} bills under Rs.450")

for b in below_450[:10]:
    # Reverse calculate rate
    # Amount = Base + Fuel(10%) + GST(18%)
    # Amount = Base * 1.298
    base = b['amount'] / 1.298
    weight = max(b['weight'], 20.0)
    rate = base / weight
    print(f"  #{b['sr']}: {b['weight']}kg → Rs.{b['amount']} (implies rate: Rs.{rate:.2f}/kg)")

print("\n" + "=" * 100)
print("KEY FINDING:")
print("=" * 100)
print("December billing DID NOT apply Rs.450 minimum LR!")
print("Example: Bill #13 charged only Rs.180 for 2.3kg shipment")
print("")
print("December appears to use formula WITHOUT minimum:")
print("  Total = Base + Fuel(10%) + GST(18%)")
print("  NO minimum Rs.450 check applied")
print("")
print("BUT the official rate card shows Rs.450 minimum LR requirement.")
print("This suggests:")
print("  Option 1: December had promotional/discounted billing (no minimum)")
print("  Option 2: Minimum LR only applies to certain shipment types")
print("  Option 3: Official rate card is newer than December billing")
print("=" * 100)
