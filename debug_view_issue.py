#!/usr/bin/env python
"""
Debug script to replicate EXACTLY what freight_calculator view does
to understand why Bigship is showing "NOT DELIVERABLE" despite returning a price
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
sys.path.insert(0, '/root/app')  # Or wherever your manage.py is

# Get the path to manage.py
import pathlib
base_dir = str(pathlib.Path(__file__).resolve().parent)
sys.path.insert(0, base_dir)

django.setup()

from forms.calculator import get_all_partner_quotes, QuoteInput, ShipmentItem

# Replicate EXACT test case from user
print("=" * 80)
print("REPLICATING VIEW BEHAVIOR FOR ODA PINCODE TEST")
print("=" * 80)

test_case = QuoteInput(
    from_pincode="560060",
    to_pincode="688529",
    items=[
        ShipmentItem(
            weight_kg=73.0,
            length_cm=1.0,
            breadth_cm=1.0,
            height_cm=1.0,
        ),
    ],
    reverse_pickup=False,
    insured_value=0.0,
    days_in_transit_storage=0,
    gst_mode='12pct',
    bigship_service_type='CFT',
)

print(f"\nTest Input:")
print(f"  From: 560060 → To: 688529")
print(f"  Weight: 73kg, Dimensions: 1×1×1 cm")
print(f"  Service: CFT")
print(f"  Items count: {len(test_case.items)}")

# Call get_all_partner_quotes EXACTLY as the view does
print("\n" + "=" * 80)
print("CALLING get_all_partner_quotes() (AS VIEW DOES)")
print("=" * 80)

results = get_all_partner_quotes(test_case)

# Check results
print(f"\nTotal results: {len(results)}")
print("\n" + "-" * 80)

for r in results:
    print(f"\n{r.partner_name}:")
    print(f"  Deliverable: {r.deliverable}")
    print(f"  Service Type: {r.rate_details.get('service_type', 'N/A')}")
    print(f"  Base Freight: ₹{r.base_freight}")
    print(f"  Surcharges: {dict(r.surcharges)}")
    print(f"  Total After GST: ₹{r.total_after_gst}")
    print(f"  Reason (if not deliverable): {r.reason}")
    
    # Check if ODA is detected
    if r.partner_name == "Bigship":
        print(f"\n  >>> BIGSHIP DETAIL:")
        print(f"      Deliverable flag: {r.deliverable}")
        print(f"      Is ODA detected: {r.rate_details.get('is_oda', 'NOT PRESENT')}")
        print(f"      Rate details: {r.rate_details}")

# Check Bigship specifically
bigship_result = next((r for r in results if r.partner_name == "Bigship"), None)
if bigship_result:
    print("\n" + "=" * 80)
    print("BIGSHIP DETAILED ANALYSIS")
    print("=" * 80)
    print(f"Deliverable: {bigship_result.deliverable}")
    if not bigship_result.deliverable:
        print(f"❌ ISSUE: Deliverable is False!")
        print(f"   Reason: {bigship_result.reason}")
    else:
        print(f"✅ Deliverable is True - should show in template")
    
    print(f"\nFull Result Object:")
    import json
    print(json.dumps(bigship_result.__dict__, indent=2, default=str))
