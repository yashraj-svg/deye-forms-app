import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import PincodeData
from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem
from forms.calculator.data_loader import PincodeDB, PincodeRecord
from forms.calculator.config import Settings

PINCODE_STATE_MAP = {
    "600095": "Tamil Nadu",
    "621220": "Tamil Nadu",
    "560060": "Karnataka",
    "676101": "Kerala",
    "695020": "Kerala",
    "524413": "Andhra Pradesh",
    "411045": "Maharashtra",
    "152116": "Punjab",
    "636111": "Tamil Nadu",
    "132039": "Haryana",
    "571134": "Karnataka",
    "201306": "Uttar Pradesh",
    "212635": "Uttar Pradesh",
    "140301": "West Bengal",
    "623536": "Tamil Nadu",
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

# Analyze failing cases
failing_cases = [
    (560060, 676101, 103.01, "CFT", 1786.4, "CFT - 103kg"),        # FAIL: Calc 2091.90
    (560060, 695020, 27.75, "CFT", 408, "CFT - 28kg"),             # FAIL: Calc 731.15
    (560060, 524413, 14.98, "MPS", 441.77, "MPS - 15kg"),          # FAIL: Calc 736.00
    (411045, 152116, 14.98, "MPS", 441.77, "MPS - 15kg DUP"),      # FAIL: Calc 736.00
    (201306, 140301, 26, "LTL", 420.96, "LTL - 26kg"),             # WARN: Calc 596.89
    (560060, 686664, 40, "CFT", 1504.30, "CFT - 40kg ODA"),        # WARN: Calc 1331.15
]

for from_pin, to_pin, weight, service_type, expected_total, desc in failing_cases:
    print("="*80)
    print(f"{desc}")
    print("="*80)
    
    inp = QuoteInput(
        items=[ShipmentItem(weight_kg=weight, length_cm=50, breadth_cm=50, height_cm=50)],
        from_pincode=str(from_pin),
        to_pincode=str(to_pin),
    )
    inp.bigship_service_type = service_type
    
    quote = calc.calculate_quote(inp, pincodes)
    
    from_rec = pincodes.get(str(from_pin))
    to_rec = pincodes.get(str(to_pin))
    
    print(f"From: {from_rec.state} -> Zone: {quote.from_zone}")
    print(f"To: {to_rec.state} -> Zone: {quote.to_zone}")
    print(f"Actual Weight: {quote.actual_weight_kg} kg")
    print(f"Chargeable Weight: {quote.chargeable_weight_kg} kg")
    print(f"Rate per kg: Rs {quote.rate_per_kg}")
    print(f"Base Freight: Rs {quote.base_freight}")
    print(f"Surcharges: {quote.surcharges}")
    print(f"Total: Rs {quote.total_after_gst}")
    print(f"Expected: Rs {expected_total}")
    print(f"Difference: Rs {abs(quote.total_after_gst - expected_total):.2f}")
    print()
