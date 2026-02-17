#!/usr/bin/env python
"""
Test script to compare CFT vs MPS charges for the same shipment
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
sys.path.insert(0, '/root/app')

import pathlib
base_dir = str(pathlib.Path(__file__).resolve().parent)
sys.path.insert(0, base_dir)

django.setup()

from forms.calculator import get_all_partner_quotes, QuoteInput, ShipmentItem

print("=" * 100)
print("COMPARING CFT vs MPS CHARGES FOR SAME SHIPMENT")
print("=" * 100)

# Same shipment: 560060 → 688529, 73kg
shipment = ShipmentItem(
    weight_kg=73.0,
    length_cm=1.0,
    breadth_cm=1.0,
    height_cm=1.0,
)

print(f"\nShipment Details:")
print(f"  From: 560060 (Karnataka)")
print(f"  To: 688529 (Alappuzha, Kerala) - ODA Location")
print(f"  Weight: 73kg")
print(f"  Dimensions: 1×1×1 cm")

# Test CFT
print("\n" + "=" * 100)
print("CFT (COLD FREIGHT TRANSPORT)")
print("=" * 100)

cft_input = QuoteInput(
    from_pincode="560060",
    to_pincode="688529",
    items=[shipment],
    reverse_pickup=False,
    insured_value=0.0,
    days_in_transit_storage=0,
    gst_mode='12pct',
    bigship_service_type='CFT',
)

cft_results = get_all_partner_quotes(cft_input)
cft_result = next((r for r in cft_results if r.partner_name == "Bigship"), None)

if cft_result and cft_result.deliverable:
    print(f"\nFrom Zone: {cft_result.from_zone}")
    print(f"To Zone: {cft_result.to_zone}")
    print(f"Chargeable Weight: {cft_result.chargeable_weight_kg}kg")
    print(f"Rate: ₹{cft_result.rate_per_kg}/kg")
    print(f"\nBreakdown:")
    print(f"  Base Freight: ₹{cft_result.base_freight}")
    print(f"  LR Charge: ₹{cft_result.surcharges.get('lr', 0)}")
    print(f"  Pickup Charge: ₹{cft_result.surcharges.get('pickup', 0)}")
    print(f"  Owner Risk: ₹{cft_result.surcharges.get('owner_risk', 0)}")
    print(f"  ODA Charge: ₹{cft_result.surcharges.get('oda', 0)}")
    print(f"  ─────────────────")
    print(f"  Total before GST: ₹{cft_result.total_before_gst}")
    print(f"  GST (18%): ₹{cft_result.gst_amount}")
    print(f"  ═════════════════")
    print(f"  TOTAL AFTER GST: ₹{cft_result.total_after_gst}")
else:
    print("❌ CFT not deliverable or error")

# Test MPS
print("\n" + "=" * 100)
print("MPS (METRO PARCEL SERVICE)")
print("=" * 100)

mps_input = QuoteInput(
    from_pincode="560060",
    to_pincode="688529",
    items=[shipment],
    reverse_pickup=False,
    insured_value=0.0,
    days_in_transit_storage=0,
    gst_mode='12pct',
    bigship_service_type='MPS',
)

mps_results = get_all_partner_quotes(mps_input)
mps_result = next((r for r in mps_results if r.partner_name == "Bigship"), None)

if mps_result:
    if mps_result.deliverable:
        print(f"\nFrom Zone: {mps_result.from_zone}")
        print(f"To Zone: {mps_result.to_zone}")
        print(f"Chargeable Weight: {mps_result.chargeable_weight_kg}kg")
        print(f"Rate: ₹{mps_result.rate_per_kg}/kg")
        print(f"\nBreakdown:")
        print(f"  Base Freight: ₹{mps_result.base_freight}")
        print(f"  LR Charge: ₹{mps_result.surcharges.get('lr', 0)}")
        print(f"  Other Surcharges: {dict((k,v) for k,v in mps_result.surcharges.items() if k != 'lr')}")
        print(f"  ─────────────────")
        print(f"  Total before GST: ₹{mps_result.total_before_gst}")
        print(f"  GST (18%): ₹{mps_result.gst_amount}")
        print(f"  ═════════════════")
        print(f"  TOTAL AFTER GST: ₹{mps_result.total_after_gst}")
    else:
        print(f"\n❌ MPS is NOT DELIVERABLE to this location")
        print(f"Reason: {mps_result.reason}")
        print(f"\nNote: MPS is Metro Parcel Service - only available in metro cities (non-ODA areas)")
else:
    print("❌ MPS error in calculation")

# Comparison
print("\n" + "=" * 100)
print("COMPARISON: CFT vs MPS")
print("=" * 100)

if cft_result and cft_result.deliverable:
    if mps_result and mps_result.deliverable:
        diff = cft_result.total_after_gst - mps_result.total_after_gst
        pct = (diff / mps_result.total_after_gst * 100) if mps_result.total_after_gst > 0 else 0
        print(f"\nCFT Total: ₹{cft_result.total_after_gst}")
        print(f"MPS Total: ₹{mps_result.total_after_gst}")
        print(f"Difference: ₹{abs(diff)} ({pct:+.1f}%)")
    else:
        print(f"\nCFT Total: ₹{cft_result.total_after_gst}")
        print(f"MPS: NOT DELIVERABLE (ODA location)")
        print(f"\n→ For ODA locations to Kerala, use CFT")
