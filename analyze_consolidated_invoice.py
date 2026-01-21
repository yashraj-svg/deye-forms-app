"""
Global Cargo Consolidated Invoice Analysis
==========================================
"""

print("=" * 90)
print("ANALYZING CONSOLIDATED GLOBAL CARGO INVOICE")
print("=" * 90)

# From the invoice
total_base = 21351.00
fuel_surcharge = 2135.00
docket_charge = 1900.00
sub_total = 25386.00
cgst = 2285.00
sgst = 2285.00
net_amount = 29956.00

print("\n📋 INVOICE SUMMARY:")
print(f"   Total Base Freight:        ₹{total_base:,.2f}")
print(f"   Fuel Surcharge @10%:       ₹{fuel_surcharge:,.2f}")
print(f"   Docket Charge:             ₹{docket_charge:,.2f}")
print(f"   ──────────────────────────────────────")
print(f"   Sub Total:                 ₹{sub_total:,.2f}")
print(f"   CGST 9%:                   ₹{cgst:,.2f}")
print(f"   SGST 9%:                   ₹{sgst:,.2f}")
print(f"   ══════════════════════════════════════")
print(f"   NET AMOUNT:                ₹{net_amount:,.2f}")

print("\n" + "─" * 90)
print("STEP-BY-STEP CALCULATION VERIFICATION:")
print("─" * 90)

# Step 1: Fuel Surcharge
print("\n1️⃣  FUEL SURCHARGE:")
calc_fuel = total_base * 0.10
print(f"   Fuel = 10% × Total Base Freight")
print(f"   Fuel = 10% × ₹{total_base:,.2f} = ₹{calc_fuel:,.2f}")
print(f"   Invoice shows: ₹{fuel_surcharge:,.2f}")
print(f"   Match: {'✓ CORRECT' if abs(calc_fuel - fuel_surcharge) < 1 else '✗ ERROR'}")

# Step 2: Docket Charge
print("\n2️⃣  DOCKET CHARGE:")
num_shipments = 21  # rows 18-38 = 21 shipments
docket_per_shipment = 1900.00 / num_shipments
print(f"   Total Docket: ₹{docket_charge:,.2f}")
print(f"   Number of shipments: {num_shipments}")
print(f"   Docket per shipment: ₹{docket_per_shipment:.2f}")
print(f"   Note: Standard docket is ₹50/shipment")
print(f"   Expected total: {num_shipments} × ₹50 = ₹{num_shipments * 50:,.2f}")
print(f"   Difference: ₹{abs(1900 - (num_shipments * 50)):,.2f}")

# Step 3: Subtotal
print("\n3️⃣  SUBTOTAL BEFORE GST:")
calc_subtotal = total_base + fuel_surcharge + docket_charge
print(f"   Subtotal = Total Base + Fuel + Docket")
print(f"   Subtotal = ₹{total_base:,.2f} + ₹{fuel_surcharge:,.2f} + ₹{docket_charge:,.2f}")
print(f"   Subtotal = ₹{calc_subtotal:,.2f}")
print(f"   Invoice shows: ₹{sub_total:,.2f}")
print(f"   Match: {'✓ CORRECT' if abs(calc_subtotal - sub_total) < 1 else '✗ ERROR'}")

# Step 4: GST (split into CGST and SGST)
print("\n4️⃣  GST CALCULATION:")
calc_cgst = sub_total * 0.09
calc_sgst = sub_total * 0.09
total_gst = cgst + sgst
calc_total_gst = calc_cgst + calc_sgst

print(f"   CGST = 9% × Subtotal = 9% × ₹{sub_total:,.2f} = ₹{calc_cgst:,.2f}")
print(f"   Invoice CGST: ₹{cgst:,.2f} {'✓' if abs(calc_cgst - cgst) < 1 else '✗'}")

print(f"\n   SGST = 9% × Subtotal = 9% × ₹{sub_total:,.2f} = ₹{calc_sgst:,.2f}")
print(f"   Invoice SGST: ₹{sgst:,.2f} {'✓' if abs(calc_sgst - sgst) < 1 else '✗'}")

print(f"\n   Total GST (CGST + SGST) = ₹{total_gst:,.2f}")
print(f"   Effective GST Rate: {(total_gst / sub_total) * 100:.1f}%")

# Step 5: Net Amount
print("\n5️⃣  NET AMOUNT:")
calc_net = sub_total + cgst + sgst
print(f"   Net Amount = Subtotal + CGST + SGST")
print(f"   Net Amount = ₹{sub_total:,.2f} + ₹{cgst:,.2f} + ₹{sgst:,.2f}")
print(f"   Net Amount = ₹{calc_net:,.2f}")
print(f"   Invoice shows: ₹{net_amount:,.2f}")
print(f"   Match: {'✓ CORRECT' if abs(calc_net - net_amount) < 1 else '✗ ERROR'}")

print("\n" + "=" * 90)
print("CONFIRMED BILLING FORMULA (CONSOLIDATED INVOICE):")
print("=" * 90)
print("""
1. Total Base Freight = Sum of all shipment base charges
2. Fuel Surcharge = 10% × Total Base Freight
3. Docket Charge = Total docket charges (shown as lump sum)
4. Subtotal = Total Base + Fuel + Docket
5. CGST = 9% × Subtotal
6. SGST = 9% × Subtotal  (Total GST = 18%)
7. Net Amount = Subtotal + CGST + SGST
""")

print("\n" + "=" * 90)
print("KEY FINDINGS:")
print("=" * 90)
print("""
✅ Fuel Surcharge:
   - Calculated on BASE FREIGHT ONLY (before docket)
   - Rate: 10%

✅ Docket Charge:
   - Added AFTER fuel surcharge
   - Shown as lump sum in consolidated invoice (₹1,900 for 21 shipments)
   - Approximately ₹90.48 per shipment (different from standard ₹50)

✅ GST Calculation:
   - Applied on (Base + Fuel + Docket)
   - Split into CGST 9% + SGST 9% = 18% total
   - DOCKET IS INCLUDED in GST base

COMPARISON WITH EARLIER INDIVIDUAL INVOICES:
Individual invoices showed: Total = Base + Fuel + GST (no docket visible)
Consolidated invoice shows: Total = Base + Fuel + Docket + GST

CONCLUSION:
- Docket charges ARE included in final billing
- Docket IS included in GST calculation
- But docket is NOT included in fuel surcharge calculation
""")

print("\n" + "=" * 90)
print("CALCULATOR UPDATE REQUIRED:")
print("=" * 90)
print("""
Current calculator needs adjustment:

❌ WRONG: Fuel = 10% × (Base + Docket + ODA)
✅ CORRECT: Fuel = 10% × (Base + ODA)

❌ WRONG: Docket not tracked separately
✅ CORRECT: Docket added after fuel, before GST

✅ CORRECT: GST = 18% × (Base + Fuel + ODA + Docket)
   (Note: GST shown as CGST 9% + SGST 9% in intrastate transactions)
""")
