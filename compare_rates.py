"""
Compare implemented rate matrix vs actual December billing rates
"""

print("=" * 100)
print("RATE MATRIX COMPARISON: IMPLEMENTED vs ACTUAL DECEMBER BILLING")
print("=" * 100)

# Implemented rates (from your attachment)
implemented_rates = {
    ("BLR", "CJB"): 13.0,
    ("BLR", "HYD"): 13.0,
    ("BLR", "BLR"): 12.0,
    ("PNQ", "LOK"): 14.0,
    ("PNQ", "BLR"): 13.0,
    ("PNQ", "CJB"): 13.0,
    ("PNQ", "MAA"): 13.0,
    ("DEL", "PNQ"): 14.0,
    ("MAA", "JAI"): 13.0,
    ("PAT", "PNQ"): 13.0,
}

# Actual rates from December bills
actual_rates = {
    ("AMB", "DEL"): 7.97,
    ("BBI", "PNQ"): 10.38,
    ("BLR", "BLR"): 11.68,  # average
    ("BLR", "CJB"): 11.96,  # average
    ("BLR", "HYD"): 13.87,
    ("BLR", "MAA"): 13.67,
    ("BLR", "PNQ"): 8.75,
    ("CJB", "BLR"): 6.55,
    ("CJB", "PNQ"): 3.85,
    ("DEL", "CCU"): 15.22,
    ("DEL", "DEL"): 77.04,  # anomaly - very small shipment
    ("DEL", "PAT"): 17.20,  # average
    ("DEL", "PNQ"): 10.00,  # average
    ("GAU", "DEL"): 9.36,
    ("LOK", "PNQ"): 10.16,  # average
    ("MAA", "JAI"): 13.38,  # average
    ("MAA", "MAA"): 10.57,
    ("PAT", "DEL"): 7.07,
    ("PAT", "PNQ"): 9.97,
    ("PNQ", "AMB"): 8.06,
    ("PNQ", "BBI"): 13.77,
    ("PNQ", "BLR"): 8.28,
    ("PNQ", "BOM"): 12.40,
    ("PNQ", "CJB"): 11.68,  # average
    ("PNQ", "DEL"): 7.22,
    ("PNQ", "MAA"): 15.01,
    ("PNQ", "NAG"): 5.04,
}

print("\nComparison for routes with both implemented and actual data:")
print("-" * 100)
print(f"{'Route':<20} {'Implemented':<15} {'Actual':<15} {'Difference':<15} {'% Diff':<10}")
print("-" * 100)

total_diff_pct = 0
count = 0

for route in sorted(set(implemented_rates.keys()) & set(actual_rates.keys())):
    impl = implemented_rates[route]
    actual = actual_rates[route]
    diff = impl - actual
    pct_diff = (diff / actual) * 100
    
    print(f"{route[0]}->{route[1]:<15} Rs.{impl:<12.2f} Rs.{actual:<12.2f} Rs.{diff:<12.2f} {pct_diff:+.1f}%")
    total_diff_pct += pct_diff
    count += 1

avg_diff_pct = total_diff_pct / count if count > 0 else 0
print("-" * 100)
print(f"Average difference: {avg_diff_pct:+.1f}% (Implemented rates are higher)")

print("\n" + "=" * 100)
print("KEY FINDINGS:")
print("=" * 100)
print(f"1. Calculator overcharges by average {avg_diff_pct:.1f}% compared to actual December billing")
print("2. Implemented matrix uses Rs.12-14/kg for most routes")
print("3. Actual rates vary widely: Rs.3.85/kg (CJB->PNQ) to Rs.15.22/kg (DEL->CCU)")
print("4. December billing shows:")
print("   - 162 bills at minimum Rs.450 (just docket, no freight)")
print("   - 28 ODA bills at minimum Rs.1050 (Rs.450 docket + Rs.600 ODA)")
print("   - 111 bills above minimum with variable zone-to-zone rates")
print("\n5. RECOMMENDED ACTIONS:")
print("   a) Replace current ZONE_RATES matrix with actual December rates")
print("   b) For missing zone pairs, use average rate Rs.10/kg or interpolate from nearby zones")
print("   c) Verify with user if December rates are standard or if there were discounts")
print("=" * 100)
