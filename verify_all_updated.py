"""
Verify all updated invoices with docket included in GST
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

# Updated invoice data with docket in GST and total
invoices = [
    {"sr": 1, "from_pin": "560060", "to_pin": "686664", "weight": 40, "base_rate": 16, "total": 1668.52},
    {"sr": 2, "from_pin": "411045", "to_pin": "226021", "weight": 131, "base_rate": 13, "total": 2260.494},
    {"sr": 3, "from_pin": "560060", "to_pin": "642103", "weight": 40, "base_rate": 14, "total": 1555.68},
    {"sr": 4, "from_pin": "411045", "to_pin": "493449", "weight": 64, "base_rate": 10, "total": 880.72},
    {"sr": 5, "from_pin": "411045", "to_pin": "148101", "weight": 20, "base_rate": 13, "total": 387.48},
    {"sr": 6, "from_pin": "560060", "to_pin": "690544", "weight": 46, "base_rate": 16, "total": 1005.328},
    {"sr": 7, "from_pin": "560060", "to_pin": "575006", "weight": 7, "base_rate": 10, "total": 140.86},
    {"sr": 8, "from_pin": "686691", "to_pin": "560060", "weight": 55, "base_rate": 16, "total": 1192.24},
    {"sr": 9, "from_pin": "560060", "to_pin": "531173", "weight": 11, "base_rate": 14, "total": 249.892},
]

print("=" * 100)
print("VERIFYING UPDATED INVOICES (Docket = ₹50, included in GST)")
print("=" * 100)

mismatches = []

for inv in invoices:
    inp = QuoteInput(
        from_pincode=inv['from_pin'],
        to_pincode=inv['to_pin'],
        weight_kg=inv['weight'],
        length_cm=0,
        breadth_cm=0,
        height_cm=0,
    )
    
    results = get_all_partner_quotes(inp)
    global_result = next((r for r in results if "Global" in r.partner_name), None)
    
    if not global_result:
        print(f"SR {inv['sr']}: ❌ No Global Cargo quote")
        mismatches.append(inv['sr'])
        continue
    
    rate_match = abs(global_result.rate_per_kg - inv['base_rate']) < 0.1
    total_match = abs(global_result.total_after_gst - inv['total']) < 1.0
    
    status = "✓" if (rate_match and total_match) else "❌"
    print(f"SR {inv['sr']}: {status} Rate: ₹{global_result.rate_per_kg:.0f}/kg (expected ₹{inv['base_rate']}) | "
          f"Total: ₹{global_result.total_after_gst:.2f} (expected ₹{inv['total']:.2f})")
    
    if not (rate_match and total_match):
        mismatches.append(inv['sr'])
        print(f"  Zone: {global_result.from_zone} → {global_result.to_zone}")

print("\n" + "=" * 100)
if mismatches:
    print(f"❌ MISMATCHES IN: SR {', '.join(map(str, mismatches))}")
else:
    print("✅ ALL INVOICES VERIFIED SUCCESSFULLY!")
print("=" * 100)
