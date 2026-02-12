from forms.calculator.data_loader import load_pincode_master
from forms.calculator.freight_calculator import GlobalCourierCargo
from forms.calculator.config import Settings

pins = load_pincode_master('.')
calc = GlobalCourierCargo(Settings())

# Check the mismatched shipments
mismatches = [
    (110020, 411045, 110, 1430),  # Excel base=1430, so rate=13/kg
    (493445, 411045, 290, 3770),  # Excel base=3770, so rate=13/kg
]

print("Checking mismatched zone rates:\n")
for from_pin, to_pin, weight, excel_base in mismatches:
    fp = pins.get(str(from_pin))
    tp = pins.get(str(to_pin))
    
    from_zone = fp.global_cargo_region if fp else 'Unknown'
    to_zone = tp.global_cargo_region if tp else 'Unknown'
    
    # Get our rate
    our_rate = calc.base_rate_per_kg(from_zone, to_zone, weight)
    excel_rate = excel_base / weight
    
    print(f"{from_pin}→{to_pin} ({weight}kg)")
    print(f"  Zones: {from_zone}→{to_zone}")
    print(f"  Excel rate: {excel_rate:.1f}/kg (base={excel_base})")
    print(f"  Our rate:   {our_rate:.1f}/kg (base={our_rate*weight:.0f})")
    print(f"  Matrix value: {calc.ZONE_RATES.get(from_zone, {}).get(to_zone, 'N/A')}")
    print()
