"""
Global Cargo (Rahul Delhivery) Rate Calculation Breakdown
=========================================================

Shipment Details:
- From Pincode: 411045
- To Pincode: 226021
- Dimensions: L=123cm, B=85cm, H=57cm
- Actual Weight: 110 KG
- Reverse Pickup: No
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import GlobalCourierCargo, QuoteInput
from forms.calculator.data_loader import load_pincode_master
from forms.calculator.config import DEFAULT_SETTINGS

# Shipment parameters
FROM_PIN = "411045"
TO_PIN = "226021"
LENGTH = 123  # cm
BREADTH = 85  # cm
HEIGHT = 57  # cm
WEIGHT = 110  # kg
REVERSE_PICKUP = False

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    print_section("GLOBAL COURIER CARGO - FREIGHT CALCULATION BREAKDOWN")
    
    # Load pincode database
    base_dir = os.path.dirname(__file__)
    pins = load_pincode_master(base_dir)
    
    # Get pincode details
    from_pin = pins.get(FROM_PIN)
    to_pin = pins.get(TO_PIN)
    
    print(f"\n📍 FROM LOCATION:")
    if from_pin:
        print(f"   Pincode: {FROM_PIN}")
        print(f"   City: {from_pin.city or 'N/A'}")
        print(f"   State: {from_pin.state or 'N/A'}")
        print(f"   Region Code: {from_pin.global_cargo_region or 'N/A'}")
    else:
        print(f"   Pincode: {FROM_PIN} (Not found in database)")
    
    print(f"\n📍 TO LOCATION:")
    if to_pin:
        print(f"   Pincode: {TO_PIN}")
        print(f"   City: {to_pin.city or 'N/A'}")
        print(f"   State: {to_pin.state or 'N/A'}")
        print(f"   Region Code: {to_pin.global_cargo_region or 'N/A'}")
        print(f"   ODA (Out of Delivery Area): {'Yes' if to_pin.is_oda else 'No'}")
        print(f"   Deliverable: {'Yes' if to_pin.deliverable else 'No'}")
    else:
        print(f"   Pincode: {TO_PIN} (Not found in database)")
    
    print_section("STEP 1: CHARGEABLE WEIGHT CALCULATION")
    
    # Volumetric weight calculation
    print(f"\n📦 Dimensions: {LENGTH} x {BREADTH} x {HEIGHT} cm")
    print(f"⚖️  Actual Weight: {WEIGHT} kg")
    
    volumetric_divisor = 4000  # As per Rahul PDF
    volumetric_weight = (LENGTH * BREADTH * HEIGHT) / volumetric_divisor
    
    print(f"\nVolumetric Weight Formula:")
    print(f"   (L × B × H) ÷ Divisor")
    print(f"   ({LENGTH} × {BREADTH} × {HEIGHT}) ÷ {volumetric_divisor}")
    print(f"   = {LENGTH * BREADTH * HEIGHT} ÷ {volumetric_divisor}")
    print(f"   = {volumetric_weight:.2f} kg")
    
    chargeable_before_min = max(WEIGHT, volumetric_weight)
    minimum_weight = 20.0  # As per Rahul PDF
    chargeable_weight = max(chargeable_before_min, minimum_weight)
    
    print(f"\nChargeable Weight = MAX(Actual, Volumetric)")
    print(f"   = MAX({WEIGHT}, {volumetric_weight:.2f})")
    print(f"   = {chargeable_before_min:.2f} kg")
    print(f"\nMinimum Weight Policy: {minimum_weight} kg")
    print(f"Final Chargeable Weight = MAX({chargeable_before_min:.2f}, {minimum_weight})")
    print(f"   = {chargeable_weight:.2f} kg")
    
    print_section("STEP 2: BASE FREIGHT CALCULATION")
    
    # Get rate per kg based on destination region
    carrier = GlobalCourierCargo(DEFAULT_SETTINGS, base_dir)
    
    to_region = to_pin.global_cargo_region if to_pin else "N/A"
    rate_per_kg = carrier.REGION_RATES.get(to_region, 13.0)
    
    print(f"\nRegion-wise Rates (Per Kg):")
    for region, rate in sorted(carrier.REGION_RATES.items()):
        marker = " ← APPLICABLE" if region == to_region else ""
        print(f"   {region}: ₹{rate}{marker}")
    
    print(f"\nDestination Region: {to_region}")
    print(f"Rate per Kg: ₹{rate_per_kg}")
    
    base_freight = rate_per_kg * chargeable_weight
    print(f"\nBase Freight = Rate × Chargeable Weight")
    print(f"   = ₹{rate_per_kg} × {chargeable_weight:.2f} kg")
    print(f"   = ₹{base_freight:.2f}")
    
    print_section("STEP 3: SURCHARGES CALCULATION")
    
    surcharges = {}
    
    # 1. Docket Charge
    docket_charge = 50.0
    surcharges['Docket Charge'] = docket_charge
    print(f"\n1️⃣  Docket Charge (Fixed): ₹{docket_charge:.2f}")
    
    # 2. ODA Charge
    oda_charge = 0.0
    if to_pin and to_pin.is_oda:
        oda_charge = 600.0
        surcharges['ODA Charge'] = oda_charge
        print(f"2️⃣  ODA Charge (Out of Delivery Area): ₹{oda_charge:.2f}")
    else:
        print(f"2️⃣  ODA Charge: ₹0.00 (Not an ODA location)")
    
    # 3. Insurance (FOV)
    insurance = 0.0
    print(f"3️⃣  Insurance (FOV): ₹0.00 (No insured value provided)")
    
    # 4. Fuel Surcharge
    subtotal_for_fuel = base_freight + docket_charge + oda_charge + insurance
    fuel_surcharge_percent = DEFAULT_SETTINGS.fuel_surcharge_global_cargo
    fuel_surcharge = fuel_surcharge_percent * subtotal_for_fuel
    surcharges['Fuel Surcharge'] = fuel_surcharge
    
    print(f"\n4️⃣  Fuel Surcharge ({fuel_surcharge_percent * 100}% on Base + Docket + ODA + Insurance):")
    print(f"   Subtotal = ₹{base_freight:.2f} + ₹{docket_charge:.2f} + ₹{oda_charge:.2f} + ₹{insurance:.2f}")
    print(f"   = ₹{subtotal_for_fuel:.2f}")
    print(f"   Fuel Surcharge = {fuel_surcharge_percent * 100}% × ₹{subtotal_for_fuel:.2f}")
    print(f"   = ₹{fuel_surcharge:.2f}")
    
    # 5. Reverse Pickup
    reverse_pickup_charge = 0.0
    if REVERSE_PICKUP:
        reverse_pickup_charge = 150.0
        surcharges['Reverse Pickup'] = reverse_pickup_charge
        print(f"\n5️⃣  Reverse Pickup: ₹{reverse_pickup_charge:.2f}")
    else:
        print(f"\n5️⃣  Reverse Pickup: ₹0.00 (Not requested)")
    
    # 6. Handling Charge
    handling_charge = 0.0
    print(f"6️⃣  Handling Charge: ₹0.00 (No piece >150kg or >6 feet)")
    
    # 7. Demurrage
    demurrage = 0.0
    print(f"7️⃣  Demurrage: ₹0.00 (No transit storage)")
    
    print(f"\n{'─' * 70}")
    print(f"Total Surcharges:")
    total_surcharges = sum(surcharges.values())
    for name, amount in surcharges.items():
        print(f"   {name}: ₹{amount:.2f}")
    print(f"{'─' * 70}")
    print(f"   TOTAL SURCHARGES: ₹{total_surcharges:.2f}")
    
    print_section("STEP 4: GST CALCULATION")
    
    total_before_gst = base_freight + total_surcharges
    gst_rate = DEFAULT_SETTINGS.gst_percent  # 18% or as configured
    gst_amount = total_before_gst * gst_rate
    
    print(f"\nTotal Before GST:")
    print(f"   Base Freight: ₹{base_freight:.2f}")
    print(f"   + Surcharges: ₹{total_surcharges:.2f}")
    print(f"   = ₹{total_before_gst:.2f}")
    
    print(f"\nGST ({gst_rate * 100}%):")
    print(f"   = {gst_rate * 100}% × ₹{total_before_gst:.2f}")
    print(f"   = ₹{gst_amount:.2f}")
    
    print_section("FINAL QUOTATION")
    
    total_after_gst = total_before_gst + gst_amount
    
    print(f"\n┌{'─' * 68}┐")
    print(f"│ {'CHARGE BREAKDOWN':<50} {'AMOUNT (₹)':>16} │")
    print(f"├{'─' * 68}┤")
    print(f"│ {'Base Freight':<50} {base_freight:>16.2f} │")
    print(f"│ {'  (Rate: ₹' + str(rate_per_kg) + '/kg × ' + str(chargeable_weight) + ' kg)':<50} {'':>16} │")
    for name, amount in surcharges.items():
        print(f"│ {name:<50} {amount:>16.2f} │")
    print(f"├{'─' * 68}┤")
    print(f"│ {'Subtotal (Before GST)':<50} {total_before_gst:>16.2f} │")
    print(f"│ {'GST @ ' + str(int(gst_rate * 100)) + '%':<50} {gst_amount:>16.2f} │")
    print(f"├{'─' * 68}┤")
    print(f"│ {'TOTAL AMOUNT PAYABLE':<50} {total_after_gst:>16.2f} │")
    print(f"└{'─' * 68}┘")
    
    print_section("VERIFICATION WITH CALCULATOR")
    
    # Run actual calculator
    inp = QuoteInput(
        from_pincode=FROM_PIN,
        to_pincode=TO_PIN,
        weight_kg=WEIGHT,
        length_cm=LENGTH,
        breadth_cm=BREADTH,
        height_cm=HEIGHT,
        reverse_pickup=REVERSE_PICKUP,
    )
    
    result = carrier.calculate_quote(inp, pins)
    
    print(f"\nCalculator Result:")
    print(f"   Partner: {result.partner_name}")
    print(f"   Deliverable: {'Yes' if result.deliverable else 'No'}")
    if not result.deliverable:
        print(f"   Reason: {result.reason}")
    else:
        print(f"   Chargeable Weight: {result.chargeable_weight_kg} kg")
        print(f"   Base Freight: ₹{result.base_freight:.2f}")
        print(f"   Surcharges: {result.surcharges}")
        print(f"   Total Before GST: ₹{result.total_before_gst:.2f}")
        print(f"   GST: ₹{result.gst_amount:.2f}")
        print(f"   Total After GST: ₹{result.total_after_gst:.2f}")
    
    print("\n" + "=" * 70)
    print()

if __name__ == "__main__":
    main()
