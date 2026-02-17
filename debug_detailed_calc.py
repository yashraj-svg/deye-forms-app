#!/usr/bin/env python3
"""Debug detailed calculation breakdown"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem, Settings
from forms.calculator.data_loader import PincodeDB, PincodeRecord

# Test pincode mappings
class TestPincodeDB(PincodeDB):
    PINCODE_STATE_MAP = {
        "600095": "Tamil Nadu", "621220": "Tamil Nadu",
        "560060": "Karnataka", "676101": "Kerala", "695020": "Kerala",
        "524413": "Andhra Pradesh", "411045": "Maharashtra",
        "152116": "Punjab", "636111": "Tamil Nadu",
        "132039": "Haryana", "571134": "Karnataka",
        "201306": "Uttar Pradesh", "212635": "Uttar Pradesh",
        "140301": "West Bengal", "623536": "Tamil Nadu",
        "686664": "Kerala",
    }
    
    def __init__(self):
        super().__init__()
        self._test_records = {}
        for pincode, state in self.PINCODE_STATE_MAP.items():
            rec = PincodeRecord(pincode=pincode)
            rec.state = state
            rec.city = ""
            self._test_records[pincode] = rec
    
    def get(self, pincode):
        if str(pincode) in self._test_records:
            return self._test_records[str(pincode)]
        return super().get(pincode)

settings = Settings()
calc = Bigship(settings=settings)
test_db = TestPincodeDB()

# Test Case 1: MPS 15kg (should NOT have pickup, should be min Rs 350 base)
print("=" * 80)
print("TEST 1: MPS 15kg Karnataka -> Andhra Pradesh")
print("Expected: Rs 441.77")
print("=" * 80)

inp = QuoteInput(
    from_pincode="560060",
    to_pincode="524413",
    items=[ShipmentItem(weight_kg=14.98, length_cm=30, breadth_cm=30, height_cm=30)],
)
inp.bigship_service_type = "MPS"

result = calc.calculate_quote(inp, test_db)

print(f"Chargeable Weight: {result.chargeable_weight_kg:.2f} kg")
print(f"From Zone: {result.from_zone}, To Zone: {result.to_zone}")
print(f"Base Freight: Rs {result.base_freight:.2f}")
print(f"Surcharges: {result.surcharges}")
print(f"Total before GST: Rs {result.total_before_gst:.2f}")
print(f"GST (18%): Rs {result.gst_amount:.2f}")
print(f"TOTAL: Rs {result.total_after_gst:.2f}")
print(f"EXPECTED: Rs 441.77")
print(f"Difference: Rs {result.total_after_gst - 441.77:.2f} ({abs(result.total_after_gst - 441.77) / 441.77 * 100:.1f}%)")

# Let me manually calculate what it SHOULD be:
print("\nMANUAL CALCULATION:")
print("Zone S1 -> S2 MPS rates: {'10kg': 269, 'add_1kg': 23}")
print(f"Base = 269 + (14.98 - 10) * 23 = 269 + 114.54 = 383.54")
print(f"Base (with min 350) = max(383.54, 350) = 383.54")
print(f"LR = 80")
print(f"Owner Risk = 0 (MPS)")
print(f"Pickup = 0 (weight < 20kg)")
print(f"ODA = 0 (MPS)")
print(f"Total before GST = 383.54 + 80 = 463.54")
print(f"GST = 463.54 * 0.18 = 83.44")
print(f"Total = 463.54 + 83.44 = 546.98")
print(f"BUT EXPECTED is Rs 441.77")
print(f"This suggests the MATRIX RATES might be wrong or ALREADY INCLUDE charges!")

# Test Case 2: CFT 103kg (has pickup, has ODA)
print("\n" + "=" * 80)
print("TEST 2: CFT 103kg Karnataka -> Kerala")
print("Expected: Rs 1786.40")
print("=" * 80)

inp = QuoteInput(
    from_pincode="560060",
    to_pincode="676101",
    items=[ShipmentItem(weight_kg=103.01, length_cm=50, breadth_cm=50, height_cm=50)],
)
inp.bigship_service_type = "CFT"

result = calc.calculate_quote(inp, test_db)

print(f"Chargeable Weight: {result.chargeable_weight_kg:.2f} kg")
print(f"From Zone: {result.from_zone}, To Zone: {result.to_zone}")
print(f"Base Freight: Rs {result.base_freight:.2f}")
print(f"Surcharges: {result.surcharges}")
print(f"Total before GST: Rs {result.total_before_gst:.2f}")
print(f"GST (18%): Rs {result.gst_amount:.2f}")
print(f"TOTAL: Rs {result.total_after_gst:.2f}")
print(f"EXPECTED: Rs 1786.40")
print(f"Difference: Rs {result.total_after_gst - 1786.40:.2f} ({abs(result.total_after_gst - 1786.40) / 1786.40 * 100:.1f}%)")

print("\nMANUAL CALCULATION:")
print("Zone S1 -> Central CFT rate: 12.92 Rs/kg")
print(f"Base = 103.01 * 12.92 = 1330.89")
print(f"Base (with min 350) = max(1330.89, 350) = 1330.89")
print(f"LR = 25")
print(f"Pickup = max(103 * 1, 75) = 103")
print(f"Owner Risk = 33")
print(f"ODA = 600 (if ODA pincode)")
print(f"Total before GST = 1330.89 + 25 + 103 + 33 + 600 = 2091.89")
print(f"GST = 2091.89 * 0.18 = 376.54")
print(f"Total = 2091.89 + 376.54 = 2468.43")
print(f"BUT EXPECTED is Rs 1786.40")
print(f"This is 682 Rs higher! ODA charge (600) is the main issue!")
