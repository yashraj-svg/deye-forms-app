#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem
from forms.calculator.data_loader import PincodeDB, PincodeRecord
from forms.calculator.config import Settings

PINCODE_STATE_MAP = {
    "600095": "Tamil Nadu",
    "621220": "Tamil Nadu",
    "560060": "Karnataka",
    "676101": "Kerala",
    "201306": "Uttar Pradesh",
    "140301": "West Bengal",
    "686664": "Kerala",
}

class TestPincodeDB(PincodeDB):
    def get(self, pincode):
        result = super().get(pincode)
        if result is None and str(pincode) in PINCODE_STATE_MAP:
            result = PincodeRecord(
                pincode=str(pincode),
                state=PINCODE_STATE_MAP[str(pincode)],
                city="Test City"
            )
        return result

settings = Settings()
calc = Bigship(settings=settings)
pincodes = TestPincodeDB()

failures = [
    (600095, 621220, 25, 74, 48, 31, "MPS", 611.29, "MPS 25kg TN→TN"),
    (560060, 676101, 103.01, 0, 0, 0, "CFT", 1786.4, "CFT 103kg KA→KL"),
    (201306, 140301, 26, 0, 0, 0, "LTL", 420.96, "LTL 26kg UP→WB"),
    (560060, 686664, 40, 0, 0, 0, "CFT", 1504.3, "CFT 40kg ODA KA→KL"),
]

for from_pin, to_pin, weight, length, breadth, height, service_type, expected, desc in failures:
    print("="*80)
    print(f"DEBUG: {desc}")
    print("="*80)
    
    # Use provided dimensions or smart defaults
    if length > 0:
        l, b, h = length, breadth, height
        dim_str = f"{l}×{b}×{h}"
    else:
        dim = max(30, (weight * 25) ** (1/3))
        l, b, h = dim, dim, dim
        dim_str = f"{l:.1f}×{b:.1f}×{h:.1f} (auto)"
    
    inp = QuoteInput(
        items=[ShipmentItem(weight_kg=weight, length_cm=l, breadth_cm=b, height_cm=h)],
        from_pincode=str(from_pin),
        to_pincode=str(to_pin),
    )
    inp.bigship_service_type = service_type
    
    result = calc.calculate_quote(inp, pincodes)
    
    from_pin_rec = pincodes.get(str(from_pin))
    to_pin_rec = pincodes.get(str(to_pin))
    from_state = from_pin_rec.state if from_pin_rec else "?"
    to_state = to_pin_rec.state if to_pin_rec else "?"
    
    print(f"\nDimensions: {dim_str} cm")
    print(f"Actual Weight: {result.actual_weight_kg} kg")
    print(f"Chargeable Weight: {result.chargeable_weight_kg} kg")
    print(f"\nBase Freight: Rs {result.base_freight}")
    print(f"Surcharges:")
    for name, amount in result.surcharges.items():
        print(f"  {name}: Rs {amount}")
    print(f"\nCalculated Total: Rs {result.total_after_gst}")
    print(f"Expected Total: Rs {expected}")
    print(f"Difference: {result.total_after_gst - expected:+.2f} (off by Rs {abs(result.total_after_gst - expected):.2f})")
    print()
