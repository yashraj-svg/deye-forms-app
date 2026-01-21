"""
Analyze the docket charge discrepancy
"""

# From the invoices:
invoices_analysis = [
    {
        "sr": 1,
        "base": 640,
        "oda": 600,
        "fuel": 124,
        "docket_shown": 50,
        "gst": 245.52,
        "total_invoice": 1609.52,
    },
    {
        "sr": 2,
        "base": 1703,
        "oda": 0,
        "fuel": 170.3,
        "docket_shown": 50,
        "gst": 337.194,
        "total_invoice": 2210.494,
    },
]

print("Analyzing docket charge inclusion in total:\n")

for inv in invoices_analysis:
    print(f"SR {inv['sr']}:")
    
    # Calculate total WITH docket
    total_with_docket = inv['base'] + inv['oda'] + inv['fuel'] + inv['docket_shown'] + inv['gst']
    print(f"  Total WITH docket: {inv['base']} + {inv['oda']} + {inv['fuel']} + {inv['docket_shown']} + {inv['gst']} = ₹{total_with_docket:.2f}")
    
    # Calculate total WITHOUT docket
    total_without_docket = inv['base'] + inv['oda'] + inv['fuel'] + inv['gst']
    print(f"  Total WITHOUT docket: {inv['base']} + {inv['oda']} + {inv['fuel']} + {inv['gst']} = ₹{total_without_docket:.2f}")
    
    print(f"  Invoice Total: ₹{inv['total_invoice']:.2f}")
    
    if abs(total_with_docket - inv['total_invoice']) < 0.01:
        print(f"  ✓ Invoice INCLUDES docket in total\n")
    elif abs(total_without_docket - inv['total_invoice']) < 0.01:
        print(f"  ✓ Invoice EXCLUDES docket from total\n")
    else:
        print(f"  ❌ Neither matches!\n")

print("\nConclusion:")
print("All invoices show docket charge (₹50) as a separate line item,")
print("but the final total DOES NOT include this amount.")
print("\nThis means either:")
print("1. Docket is waived/not charged for these shipments")
print("2. Docket is shown for reference but not actually billed")
print("3. These are different invoice types (maybe consolidated)")
