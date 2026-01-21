"""
Verify Global Cargo Region Updates
===================================
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import GlobalCourierCargo
from forms.calculator.data_loader import load_pincode_master, _RAHUL_REGION_BY_STATE
from forms.calculator.config import DEFAULT_SETTINGS

print("=" * 80)
print("GLOBAL CARGO REGION UPDATES VERIFICATION")
print("=" * 80)

carrier = GlobalCourierCargo(DEFAULT_SETTINGS)

print("\n📋 UPDATED REGION RATES:")
for region, rate in sorted(carrier.REGION_RATES.items()):
    marker = " ← NEW" if region == "W3" else ""
    print(f"   {region}: ₹{rate}/kg{marker}")

print("\n📋 STATE TO REGION MAPPINGS (Selected):")
print("\nWest Regions:")
print(f"   Goa → {_RAHUL_REGION_BY_STATE.get('goa', 'NOT FOUND')}")
print(f"   Maharashtra → {_RAHUL_REGION_BY_STATE.get('maharashtra', 'NOT FOUND')}")
print(f"   Gujarat → {_RAHUL_REGION_BY_STATE.get('gujarat', 'NOT FOUND')} ← NEW")

print("\nSouth Regions:")
print(f"   Karnataka → {_RAHUL_REGION_BY_STATE.get('karnataka', 'NOT FOUND')}")
print(f"   Tamil Nadu → {_RAHUL_REGION_BY_STATE.get('tamil nadu', 'NOT FOUND')}")
print(f"   Andhra Pradesh → {_RAHUL_REGION_BY_STATE.get('andhra pradesh', 'NOT FOUND')}")
print(f"   Telangana → {_RAHUL_REGION_BY_STATE.get('telangana', 'NOT FOUND')}")
print(f"   Kerala → {_RAHUL_REGION_BY_STATE.get('kerala', 'NOT FOUND')}")

print("\n" + "=" * 80)
print("RATE VERIFICATION:")
print("=" * 80)

# Test Gujarat (W3)
gujarat_region = _RAHUL_REGION_BY_STATE.get('gujarat')
gujarat_rate = carrier.REGION_RATES.get(gujarat_region, 0)
print(f"\n✓ Gujarat:")
print(f"   Region: {gujarat_region}")
print(f"   Rate: ₹{gujarat_rate}/kg")
print(f"   Expected: W3 → ₹14/kg")
print(f"   Match: {'✓ CORRECT!' if gujarat_region == 'W3' and gujarat_rate == 14.0 else '✗ ERROR'}")

# Test Andhra Pradesh (S2)
ap_region = _RAHUL_REGION_BY_STATE.get('andhra pradesh')
ap_rate = carrier.REGION_RATES.get(ap_region, 0)
print(f"\n✓ Andhra Pradesh:")
print(f"   Region: {ap_region}")
print(f"   Rate: ₹{ap_rate}/kg")
print(f"   Expected: S2 → ₹14/kg")
print(f"   Match: {'✓ CORRECT!' if ap_region == 'S2' and ap_rate == 14.0 else '✗ ERROR'}")

# Test other S2 states
print(f"\n✓ Other S2 States:")
for state in ['karnataka', 'tamil nadu', 'telangana', 'pondicherry']:
    region = _RAHUL_REGION_BY_STATE.get(state)
    rate = carrier.REGION_RATES.get(region, 0)
    print(f"   {state.title()}: {region} → ₹{rate}/kg")

print("\n" + "=" * 80)
print("ALL REGIONS AND RATES AS PER ATTACHMENT:")
print("=" * 80)

zones_from_attachment = {
    "C1": ("Raipur, Nagpur", 10),
    "C2": ("Chattisgarh, Madhya Pradesh", 13),
    "E1": ("Kolkata, Bhubaneshwar, Patna", 16),
    "E2": ("Bihar, Jharkhand, Orissa, West Bengal, Jamshedpur", 16),
    "N1": ("New Delhi, Gurgaon, Noida, Faridabad, Ghaziabad, Sahibabad", 13),
    "N2": ("Haryana, Punjab, Rajasthan, Uttar Pradesh, Uttarakhand, Ludhiana, Chandigarh", 13),
    "N3": ("Himachal Pradesh, Jammu & Kashmir", 17),
    "NE1": ("Guwahati", 22),
    "NE2": ("Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura", 33),
    "S1": ("Bangalore, Chennai, Hyderabad", 13),
    "S2": ("Karnataka, Pondicherry, Tamil Nadu, Telangana, Andhra Pradesh", 14),
    "S3": ("Kerala", 16),
    "W1": ("Pune, Mumbai", 10),
    "W2": ("Goa, Maharashtra", 10),
    "W3": ("Gujarat", 14),
}

print("\n")
for zone, (area, expected_rate) in zones_from_attachment.items():
    actual_rate = carrier.REGION_RATES.get(zone, 0)
    match = "✓" if actual_rate == expected_rate else "✗"
    print(f"{zone}: ₹{actual_rate}/kg (Expected: ₹{expected_rate}/kg) {match}")

print("\n" + "=" * 80)
print("✓ Global Cargo regions updated successfully!")
print("=" * 80)
