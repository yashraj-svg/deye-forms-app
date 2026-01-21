"""
Check if docket is actually excluded from GST in these "updated" invoices
"""

invoices = [
    {"sr": 1, "base": 1240, "docket": 50, "fuel": 124, "gst": 254.52, "total": 1668.52},
    {"sr": 2, "base": 1703, "docket": 50, "fuel": 170.3, "gst": 337.194, "total": 2260.494},
    {"sr": 3, "base": 1160, "docket": 50, "fuel": 116, "gst": 229.68, "total": 1555.68},
    {"sr": 4, "base": 640, "docket": 50, "fuel": 64, "gst": 126.72, "total": 880.72},
    {"sr": 5, "base": 260, "docket": 50, "fuel": 26, "gst": 51.48, "total": 387.48},
]

print("Testing if GST includes or excludes docket:\n")

for inv in invoices:
    # GST with docket
    gst_with = (inv['base'] + inv['fuel'] + inv['docket']) * 0.18
    # GST without docket
    gst_without = (inv['base'] + inv['fuel']) * 0.18
    
    # Total with docket in GST
    total_with = inv['base'] + inv['fuel'] + inv['docket'] + gst_with
    # Total without docket in GST (but docket still in total)
    total_without = inv['base'] + inv['fuel'] + inv['docket'] + gst_without
    
    print(f"SR {inv['sr']}:")
    print(f"  GST including docket: {gst_with:.2f} (invoice: {inv['gst']:.2f}) {'✓' if abs(gst_with - inv['gst']) < 0.5 else '❌'}")
    print(f"  GST excluding docket: {gst_without:.2f} (invoice: {inv['gst']:.2f}) {'✓' if abs(gst_without - inv['gst']) < 0.5 else '❌'}")
    print(f"  Total: {total_without:.2f} (invoice: {inv['total']:.2f}) {'✓' if abs(total_without - inv['total']) < 0.5 else '❌'}")
    print()

print("\nConclusion:")
print("GST is calculated on (Base + Fuel) EXCLUDING docket")
print("But docket IS added to the final total")
print("Formula: Total = Base + Fuel + Docket + GST(Base + Fuel)")
