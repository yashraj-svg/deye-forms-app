"""
Test Global Cargo quote for 574214 to verify ODA charge appears
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

print("=" * 100)
print("TESTING ODA CHARGE FOR PINCODE 574214")
print("=" * 100)

# Test shipment to 574214
inp = QuoteInput(
    from_pincode="560060",  # Bangalore
    to_pincode="574214",    # Should be ODA
    weight_kg=12.0,
    length_cm=20,
    breadth_cm=20,
    height_cm=20,
)

print("\nShipment Details:")
print(f"  From: 560060 (Bangalore)")
print(f"  To: 574214 (Belthangady, Karnataka - Should be ODA)")
print(f"  Weight: 12kg")

results = get_all_partner_quotes(inp)
gc = next((r for r in results if "Global" in r.partner_name), None)

if gc:
    print(f"\n{'-' * 100}")
    print(f"GLOBAL CARGO QUOTE:")
    print(f"{'-' * 100}")
    print(f"Route: {gc.from_zone} -> {gc.to_zone}")
    print(f"Deliverable: {gc.deliverable}")
    print(f"Base Freight: Rs.{gc.base_freight}")
    print(f"\nSurcharges:")
    if gc.surcharges:
        for key, value in gc.surcharges.items():
            print(f"  {key}: Rs.{value}")
        
        if 'oda' in gc.surcharges:
            print(f"\n*** ODA CHARGE FOUND: Rs.{gc.surcharges['oda']} ***")
        else:
            print(f"\n*** WARNING: ODA CHARGE MISSING! ***")
    else:
        print(f"  None")
        print(f"\n*** WARNING: NO SURCHARGES AT ALL! ***")
    
    print(f"\nGST: Rs.{gc.gst_amount}")
    print(f"TOTAL: Rs.{gc.total_after_gst}")
else:
    print("\nERROR: No Global Cargo quote generated!")

# Also test a few other known ODA pincodes
print(f"\n\n{'-' * 100}")
print("TESTING OTHER KNOWN ODA PINCODES:")
print(f"{'-' * 100}")

test_pincodes = [
    ('574227', 'Moodabidri'),
    ('686610', 'Kottayam'),
    ('690518', 'Kollam'),
]

for pin, city in test_pincodes:
    inp_test = QuoteInput(
        from_pincode="560060",
        to_pincode=pin,
        weight_kg=20.0,
        length_cm=20, breadth_cm=20, height_cm=20,
    )
    
    results_test = get_all_partner_quotes(inp_test)
    gc_test = next((r for r in results_test if "Global" in r.partner_name), None)
    
    if gc_test and 'oda' in gc_test.surcharges:
        print(f"{pin} ({city}): ODA Rs.{gc_test.surcharges['oda']} - OK")
    elif gc_test:
        print(f"{pin} ({city}): NO ODA CHARGE - PROBLEM!")
    else:
        print(f"{pin} ({city}): NO QUOTE GENERATED - ERROR!")

print("=" * 100)
