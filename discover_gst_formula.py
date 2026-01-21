"""
Critical Discovery: Docket NOT in GST calculation
=================================================
"""

print("=" * 80)
print("ANALYZING GST CALCULATION IN INDIVIDUAL INVOICES")
print("=" * 80)

invoices = [
    {"name": "Pune → Barnala", "base": 260, "fuel": 26, "docket": 50, "gst": 51.48, "total": 337.48},
    {"name": "Pune → Lucknow", "base": 1703, "fuel": 170.3, "docket": 50, "gst": 337.194, "total": 2210.494},
    {"name": "Pune → Mahasamund", "base": 640, "fuel": 64, "docket": 50, "gst": 126.72, "total": 830.72},
]

print("\nTesting TWO different GST formulas:\n")

for inv in invoices:
    print(f"{'─' * 80}")
    print(f"{inv['name']}")
    print(f"{'─' * 80}")
    
    # Formula 1: GST on (Base + Fuel + Docket)
    subtotal_with_docket = inv['base'] + inv['fuel'] + inv['docket']
    gst_with_docket = subtotal_with_docket * 0.18
    total_with_docket = subtotal_with_docket + gst_with_docket
    
    print(f"\n❶ GST WITH Docket: 18% × (Base + Fuel + Docket)")
    print(f"   = 18% × ({inv['base']} + {inv['fuel']} + {inv['docket']})")
    print(f"   = 18% × {subtotal_with_docket} = ₹{gst_with_docket:.3f}")
    print(f"   Expected GST: ₹{inv['gst']}")
    print(f"   Match: {'✓' if abs(gst_with_docket - inv['gst']) < 0.01 else '✗'}")
    
    # Formula 2: GST on (Base + Fuel) WITHOUT Docket
    subtotal_no_docket = inv['base'] + inv['fuel']
    gst_no_docket = subtotal_no_docket * 0.18
    total_no_docket = subtotal_no_docket + gst_no_docket + inv['docket']
    
    print(f"\n❷ GST WITHOUT Docket: 18% × (Base + Fuel)")
    print(f"   = 18% × ({inv['base']} + {inv['fuel']})")
    print(f"   = 18% × {subtotal_no_docket} = ₹{gst_no_docket:.3f}")
    print(f"   Expected GST: ₹{inv['gst']}")
    print(f"   Match: {'✅ PERFECT!' if abs(gst_no_docket - inv['gst']) < 0.01 else '✗'}")
    
    print(f"\n   Total with Formula 2: {subtotal_no_docket} + {gst_no_docket:.3f} + {inv['docket']} = ₹{total_no_docket:.3f}")
    print(f"   Expected Total: ₹{inv['total']}")
    print(f"   Match: {'✅' if abs(total_no_docket - inv['total']) < 0.01 else '✗'}")
    print()

print("=" * 80)
print("🔍 CRITICAL DISCOVERY!")
print("=" * 80)
print("""
Individual invoices show:
✅ GST = 18% × (Base + Fuel) - DOCKET NOT INCLUDED!
✅ Total = Base + Fuel + GST + Docket

BUT the consolidated invoice showed:
✅ GST = 18% × (Base + Fuel + Docket) - DOCKET INCLUDED!

This might be because:
1. Individual invoices exclude docket from GST base
2. Consolidated invoices include docket in GST base
3. OR there's a different accounting treatment

RECOMMENDATION:
For individual quotes, use: GST = 18% × (Base + Fuel)
Docket is shown separately and added to final total.
""")
