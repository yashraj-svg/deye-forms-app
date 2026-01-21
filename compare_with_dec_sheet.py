"""
Compare updated calculator with actual December billing
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

print("=" * 120)
print("DECEMBER BILLING COMPARISON - UPDATED CALCULATOR vs ACTUAL BILLS")
print("=" * 120)

matches = []
mismatches = []
errors = []

for i, bill in enumerate(bills[:50], 1):  # Test first 50 bills
    if not bill['from_pin'] or not bill['to_pin'] or bill['from_pin'] == '#N/A':
        continue
    
    try:
        inp = QuoteInput(
            from_pincode=bill['from_pin'],
            to_pincode=bill['to_pin'],
            weight_kg=bill['weight'],
            length_cm=0, breadth_cm=0, height_cm=0,
        )
        
        results = get_all_partner_quotes(inp)
        gc = next((r for r in results if "Global" in r.partner_name), None)
        
        if gc:
            actual = bill['amount']
            calculated = gc.total_after_gst
            diff = calculated - actual
            diff_pct = (diff / actual * 100) if actual > 0 else 0
            
            # Consider match if within Rs.5 or 2%
            if abs(diff) <= 5 or abs(diff_pct) <= 2:
                matches.append({
                    'bill': bill,
                    'actual': actual,
                    'calculated': calculated,
                    'diff': diff,
                })
            else:
                mismatches.append({
                    'bill': bill,
                    'actual': actual,
                    'calculated': calculated,
                    'diff': diff,
                    'diff_pct': diff_pct,
                    'gc': gc,
                })
    except Exception as e:
        errors.append({'bill': bill, 'error': str(e)})

print(f"\nResults Summary (first 50 bills):")
print(f"  Matches (within Rs.5 or 2%): {len(matches)}")
print(f"  Mismatches: {len(mismatches)}")
print(f"  Errors: {len(errors)}")

if matches:
    print(f"\n{'─' * 120}")
    print(f"SAMPLE MATCHES (Calculator accurate within Rs.5):")
    print(f"{'─' * 120}")
    for m in matches[:5]:
        b = m['bill']
        print(f"Bill #{b['sr']}: {b['from_pin']} → {b['to_pin']}, {b['weight']}kg")
        print(f"  Actual: Rs.{m['actual']:.2f} | Calculated: Rs.{m['calculated']:.2f} | Diff: Rs.{m['diff']:.2f}")

if mismatches:
    print(f"\n{'─' * 120}")
    print(f"MISMATCHES - Requires Investigation:")
    print(f"{'─' * 120}")
    for m in mismatches[:10]:
        b = m['bill']
        gc = m['gc']
        print(f"\nBill #{b['sr']}: {b['from_pin']} → {b['to_pin']}, {b['weight']}kg, Mode: {b['mode']}")
        print(f"  Actual Bill: Rs.{m['actual']:.2f}")
        print(f"  Calculator:  Rs.{m['calculated']:.2f}")
        print(f"  Difference:  Rs.{m['diff']:.2f} ({m['diff_pct']:+.1f}%)")
        
        if gc:
            print(f"  Calculator breakdown:")
            print(f"    Zone: {gc.from_zone} → {gc.to_zone}, Rate: Rs.{gc.rate_per_kg}/kg")
            print(f"    Chargeable: {gc.chargeable_weight_kg}kg, Base: Rs.{gc.base_freight}")
            print(f"    Surcharges: {gc.surcharges}")
            print(f"    GST: Rs.{gc.gst_amount}")

# Analyze mismatch patterns
if mismatches:
    print(f"\n{'─' * 120}")
    print(f"MISMATCH ANALYSIS:")
    print(f"{'─' * 120}")
    
    overcharge_count = sum(1 for m in mismatches if m['diff'] > 0)
    undercharge_count = sum(1 for m in mismatches if m['diff'] < 0)
    avg_diff = sum(m['diff'] for m in mismatches) / len(mismatches)
    avg_diff_pct = sum(m['diff_pct'] for m in mismatches) / len(mismatches)
    
    print(f"Calculator overcharges: {overcharge_count} bills")
    print(f"Calculator undercharges: {undercharge_count} bills")
    print(f"Average difference: Rs.{avg_diff:.2f} ({avg_diff_pct:+.1f}%)")
    
    # Check if minimum LR is the issue
    minimum_lr_issues = sum(1 for m in mismatches if m['calculated'] == 450.0 and m['actual'] < 450.0)
    if minimum_lr_issues:
        print(f"\nPotential minimum LR issues: {minimum_lr_issues} bills where calculator=Rs.450 but actual<Rs.450")

print(f"\n{'=' * 120}")
print(f"CONCLUSION:")
print(f"{'=' * 120}")

total_tested = len(matches) + len(mismatches)
accuracy_pct = (len(matches) / total_tested * 100) if total_tested > 0 else 0

print(f"Accuracy rate: {accuracy_pct:.1f}% of bills match within Rs.5 tolerance")
if accuracy_pct >= 90:
    print(f"EXCELLENT - Calculator is highly accurate")
elif accuracy_pct >= 70:
    print(f"GOOD - Minor adjustments may be needed")
else:
    print(f"NEEDS REVIEW - Significant differences found")
    print(f"\nPossible reasons for mismatches:")
    print(f"  1. December may have had special discounted rates")
    print(f"  2. Actual bills may include manual adjustments")
    print(f"  3. Some zones may have different rates than official matrix")
    print(f"  4. ODA charges may vary by location")

print(f"{'=' * 120}")
