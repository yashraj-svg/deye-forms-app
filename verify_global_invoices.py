"""
Global Cargo Invoice Verification
==================================
Comparing actual invoices with calculator logic
"""

print("=" * 90)
print("ANALYZING GLOBAL CARGO ACTUAL INVOICES")
print("=" * 90)

invoices = [
    {"lr": "11083910704944", "from": "Bangalore", "to": "Kanjiramoto", "from_pin": "560060", "to_pin": "686664", 
     "rate": 16, "weight": 40, "oda": 600, "total_base": 1240, "docket": 50, "fuel": 124, "gst": 245.52, "total": 1609.52},
    {"lr": "11083910707770", "from": "Pune", "to": "Lucknow", "from_pin": "411045", "to_pin": "226021",
     "rate": 13, "weight": 131, "oda": 0, "total_base": 1703, "docket": 50, "fuel": 170.3, "gst": 337.194, "total": 2210.494},
    {"lr": "11083910704885", "from": "Bangalore", "to": "Polechi", "from_pin": "560060", "to_pin": "642103",
     "rate": 14, "weight": 40, "oda": 600, "total_base": 1160, "docket": 50, "fuel": 116, "gst": 229.68, "total": 1505.68},
    {"lr": "11083910707836", "from": "Pune", "to": "Mahasamund", "from_pin": "411045", "to_pin": "493449",
     "rate": 10, "weight": 64, "oda": 0, "total_base": 640, "docket": 50, "fuel": 64, "gst": 126.72, "total": 830.72},
    {"lr": "11083910707976", "from": "Pune", "to": "Barnala", "from_pin": "411045", "to_pin": "148101",
     "rate": 13, "weight": 20, "oda": 0, "total_base": 260, "docket": 50, "fuel": 26, "gst": 51.48, "total": 337.48},
    {"lr": "11083910708632", "from": "Bangalore", "to": "Kollam", "from_pin": "560060", "to_pin": "690544",
     "rate": 16, "weight": 46, "oda": 0, "total_base": 736, "docket": 50, "fuel": 73.6, "gst": 145.728, "total": 955.328},
    {"lr": "13090321447892", "from": "Bangalore", "to": "Mangaluru", "from_pin": "560060", "to_pin": "575006",
     "rate": 10, "weight": 7, "oda": 0, "total_base": 70, "docket": 50, "fuel": 7, "gst": 13.86, "total": 90.86},
    {"lr": "11083910708934", "from": "Perumbavoor", "to": "Bangalore", "from_pin": "686691", "to_pin": "560060",
     "rate": 16, "weight": 55, "oda": 0, "total_base": 880, "docket": 50, "fuel": 88, "gst": 174.24, "total": 1142.24},
    {"lr": "13090321314155", "from": "Banglore", "to": "Visakhapatam", "from_pin": "560060", "to_pin": "531173",
     "rate": 14, "weight": 11, "oda": 0, "total_base": 154, "docket": 50, "fuel": 15.4, "gst": 30.492, "total": 199.892},
]

print("\nTesting invoice calculation formula:\n")

for idx, inv in enumerate(invoices, 1):
    print(f"{'─' * 90}")
    print(f"Invoice #{idx}: {inv['from']} → {inv['to']}")
    print(f"{'─' * 90}")
    
    # Calculate base freight
    base_freight = inv['weight'] * inv['rate']
    print(f"Base Freight = {inv['weight']} kg × ₹{inv['rate']}/kg = ₹{base_freight}")
    
    # Total Base = Base Freight + ODA
    calc_total_base = base_freight + inv['oda']
    print(f"Total Base = {base_freight} + {inv['oda']} (ODA) = ₹{calc_total_base}")
    print(f"Actual Total Base: ₹{inv['total_base']} {'✓' if abs(calc_total_base - inv['total_base']) < 0.01 else '✗'}")
    
    # Fuel = 10% × Total Base
    calc_fuel = inv['total_base'] * 0.10
    print(f"\nFuel = 10% × {inv['total_base']} = ₹{calc_fuel:.2f}")
    print(f"Actual Fuel: ₹{inv['fuel']} {'✓' if abs(calc_fuel - inv['fuel']) < 0.01 else '✗'}")
    
    # Test different GST formulas
    print(f"\nTesting GST formulas:")
    
    # Formula 1: GST on (Total Base + Fuel) - NO DOCKET
    gst_formula1 = (inv['total_base'] + inv['fuel']) * 0.18
    print(f"  Formula 1: 18% × (Total Base + Fuel)")
    print(f"           = 18% × ({inv['total_base']} + {inv['fuel']}) = ₹{gst_formula1:.3f}")
    print(f"           Actual: ₹{inv['gst']} {'✓ MATCH!' if abs(gst_formula1 - inv['gst']) < 0.01 else '✗'}")
    
    # Formula 2: GST on (Total Base + Fuel + Docket)
    gst_formula2 = (inv['total_base'] + inv['fuel'] + inv['docket']) * 0.18
    print(f"  Formula 2: 18% × (Total Base + Fuel + Docket)")
    print(f"           = 18% × ({inv['total_base']} + {inv['fuel']} + {inv['docket']}) = ₹{gst_formula2:.3f}")
    print(f"           {'✓ MATCH!' if abs(gst_formula2 - inv['gst']) < 0.01 else '✗'}")
    
    # Calculate total
    calc_total_no_docket = inv['total_base'] + inv['fuel'] + inv['gst']
    calc_total_with_docket = inv['total_base'] + inv['fuel'] + inv['docket'] + inv['gst']
    
    print(f"\nTotal Calculation:")
    print(f"  Without Docket: {inv['total_base']} + {inv['fuel']} + {inv['gst']} = ₹{calc_total_no_docket:.3f}")
    print(f"  With Docket: {inv['total_base']} + {inv['fuel']} + {inv['docket']} + {inv['gst']} = ₹{calc_total_with_docket:.3f}")
    print(f"  Actual Total: ₹{inv['total']} {'✓' if abs(calc_total_no_docket - inv['total']) < 0.01 else ('✓' if abs(calc_total_with_docket - inv['total']) < 0.01 else '✗')}")
    
    print()

print("\n" + "=" * 90)
print("CONFIRMED GLOBAL CARGO BILLING FORMULA:")
print("=" * 90)
print("""
1. Base Freight = Weight × Rate per kg
2. Total Base = Base Freight + ODA Charges
3. Fuel Surcharge = 10% × Total Base
4. Subtotal for GST = Total Base + Fuel (NO DOCKET in GST calculation)
5. GST = 18% × Subtotal
6. Final Total = Total Base + Fuel + GST (Docket shown separately)

KEY FINDING: Docket charge is NOT included in GST calculation!
This is different from our calculator which includes docket in fuel calculation.
""")

print("\n" + "=" * 90)
print("ISSUES WITH CURRENT CALCULATOR:")
print("=" * 90)
print("""
❌ Current Calculator:
   - Includes Docket (₹50) in fuel surcharge calculation
   - Fuel = 10% × (Base + Docket + ODA + Insurance)
   
✅ Actual Billing:
   - Docket is NOT included in fuel calculation
   - Fuel = 10% × (Base + ODA only)
   - Docket is NOT included in GST calculation
   - GST = 18% × (Base + ODA + Fuel)

REQUIRED CHANGES:
1. Remove Docket from fuel surcharge calculation
2. Remove Docket from GST calculation
3. Add Docket at the end (after GST)
""")
