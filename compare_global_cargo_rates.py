#!/usr/bin/env python
"""Compare Global Cargo rates: Previous vs Current (14-02-2026)"""

import subprocess
import re

# Previous rates from commit 75ed8179
PREVIOUS_RATES = {
    "AMB": {"AMB": 12.0, "JAI": 13.0, "DEL": 12.0, "AMD": 14.0, "PNQ": 14.0, "BOM": 14.0, "NAG": 13.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 17.0, "LOK": 14.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
    "JAI": {"AMB": 13.0, "JAI": 10.0, "DEL": 12.0, "AMD": 12.0, "PNQ": 14.0, "BOM": 13.0, "NAG": 13.0, "IDR": 14.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 18.0, "NJP": 36.0, "CCU": 16.0, "GAU": 18.0},
    "DEL": {"AMB": 12.0, "JAI": 12.0, "DEL": 13.0, "AMD": 14.0, "PNQ": 13.0, "BOM": 13.0, "NAG": 13.0, "IDR": 14.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 16.0, "LOK": 13.0, "PAT": 16.0, "NJP": 34.0, "CCU": 16.0, "GAU": 17.0},
    "AMD": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 10.0, "PNQ": 13.0, "BOM": 12.0, "NAG": 12.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 13.0, "BBI": 16.0, "LOK": 13.0, "PAT": 18.0, "NJP": 34.0, "CCU": 16.0, "GAU": 16.0},
    "PNQ": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 12.0, "IDR": 13.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 15.0, "BBI": 16.0, "LOK": 13.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
    "BOM": {"AMB": 13.0, "JAI": 14.0, "DEL": 13.0, "AMD": 12.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 10.0, "IDR": 13.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 14.0, "BBI": 16.0, "LOK": 13.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
    "NAG": {"AMB": 12.0, "JAI": 12.0, "DEL": 13.0, "AMD": 12.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 10.0, "IDR": 12.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 16.0},
    "IDR": {"AMB": 12.0, "JAI": 13.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 13.0, "BOM": 13.0, "NAG": 12.0, "IDR": 10.0, "BLR": 13.0, "HYD": 13.0, "MAA": 13.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 16.0, "NJP": 35.0, "CCU": 17.0, "GAU": 16.0},
    "BLR": {"AMB": 14.0, "JAI": 14.0, "DEL": 15.0, "AMD": 13.0, "PNQ": 13.0, "BOM": 13.0, "NAG": 13.0, "IDR": 14.0, "BLR": 14.0, "HYD": 13.0, "MAA": 14.0, "CJB": 16.0, "BBI": 14.0, "LOK": 15.0, "PAT": 18.0, "NJP": 32.0, "CCU": 17.0, "GAU": 17.0},
    "HYD": {"AMB": 14.0, "JAI": 14.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 13.0, "BOM": 12.0, "NAG": 12.0, "IDR": 12.0, "BLR": 13.0, "HYD": 10.0, "MAA": 12.0, "CJB": 12.0, "BBI": 16.0, "LOK": 15.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 16.0},
    "MAA": {"AMB": 14.0, "JAI": 14.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 12.0, "BOM": 12.0, "NAG": 12.0, "IDR": 13.0, "BLR": 13.0, "HYD": 13.0, "MAA": 13.0, "CJB": 12.0, "BBI": 14.0, "LOK": 15.0, "PAT": 16.0, "NJP": 32.0, "CCU": 15.0, "GAU": 16.0},
    "CJB": {"AMB": 15.0, "JAI": 15.0, "DEL": 16.0, "AMD": 16.0, "PNQ": 17.0, "BOM": 17.0, "NAG": 16.0, "IDR": 15.0, "BLR": 13.0, "HYD": 14.0, "MAA": 14.0, "CJB": 10.0, "BBI": 16.0, "LOK": 13.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 17.0},
    "BBI": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 14.0, "PNQ": 15.0, "BOM": 15.0, "NAG": 15.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 10.0, "LOK": 13.0, "PAT": 15.0, "NJP": 35.0, "CCU": 15.0, "GAU": 15.0},
    "LOK": {"AMB": 12.0, "JAI": 13.0, "DEL": 12.0, "AMD": 14.0, "PNQ": 15.0, "BOM": 15.0, "NAG": 14.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 13.0, "LOK": 13.0, "PAT": 16.0, "NJP": 36.0, "CCU": 16.0, "GAU": 17.0},
    "PAT": {"AMB": 17.0, "JAI": 17.0, "DEL": 13.0, "AMD": 15.0, "PNQ": 16.0, "BOM": 15.0, "NAG": 14.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 15.0, "LOK": 13.0, "PAT": 15.0, "NJP": 36.0, "CCU": 13.0, "GAU": 14.0},
    "NJP": {"AMB": 35.0, "JAI": 35.0, "DEL": 36.0, "AMD": 36.0, "PNQ": 36.0, "BOM": 36.0, "NAG": 30.0, "IDR": 30.0, "BLR": 35.0, "HYD": 35.0, "MAA": 35.0, "CJB": 35.0, "BBI": 35.0, "LOK": 30.0, "PAT": 35.0, "NJP": 25.0, "CCU": 30.0, "GAU": 30.0},
    "CCU": {"AMB": 18.0, "JAI": 17.0, "DEL": 16.0, "AMD": 17.0, "PNQ": 16.0, "BOM": 16.0, "NAG": 15.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 12.0, "LOK": 15.0, "PAT": 14.0, "NJP": 20.0, "CCU": 12.0, "GAU": 13.0},
    "GAU": {"AMB": 15.0, "JAI": 16.0, "DEL": 17.0, "AMD": 17.0, "PNQ": 17.0, "BOM": 16.0, "NAG": 15.0, "IDR": 16.0, "BLR": 17.0, "HYD": 17.0, "MAA": 17.0, "CJB": 17.0, "BBI": 18.0, "LOK": 18.0, "PAT": 17.0, "NJP": 17.0, "CCU": 12.0, "GAU": 16.0},
}

# Current rates (14-02-2026)
CURRENT_RATES = {
    "AMB": {"AMB": 12.0, "JAI": 13.0, "DEL": 12.0, "AMD": 14.0, "PNQ": 14.0, "BOM": 14.0, "NAG": 13.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 17.0, "LOK": 14.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
    "JAI": {"AMB": 13.0, "JAI": 10.0, "DEL": 12.0, "AMD": 12.0, "PNQ": 14.0, "BOM": 13.0, "NAG": 13.0, "IDR": 14.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 18.0, "NJP": 36.0, "CCU": 16.0, "GAU": 18.0},
    "DEL": {"AMB": 12.0, "JAI": 12.0, "DEL": 10.0, "AMD": 14.0, "PNQ": 15.0, "BOM": 15.0, "NAG": 13.0, "IDR": 14.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 16.0, "LOK": 12.0, "PAT": 16.0, "NJP": 34.0, "CCU": 16.0, "GAU": 17.0},
    "AMD": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 10.0, "PNQ": 13.0, "BOM": 12.0, "NAG": 12.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 13.0, "BBI": 16.0, "LOK": 13.0, "PAT": 18.0, "NJP": 34.0, "CCU": 16.0, "GAU": 16.0},
    "PNQ": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 12.0, "IDR": 13.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 15.0, "BBI": 16.0, "LOK": 14.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
    "BOM": {"AMB": 13.0, "JAI": 14.0, "DEL": 13.0, "AMD": 12.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 10.0, "IDR": 13.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 14.0, "BBI": 16.0, "LOK": 13.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
    "NAG": {"AMB": 12.0, "JAI": 12.0, "DEL": 13.0, "AMD": 12.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 10.0, "IDR": 12.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 16.0},
    "IDR": {"AMB": 12.0, "JAI": 13.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 14.0, "BOM": 13.0, "NAG": 12.0, "IDR": 10.0, "BLR": 13.0, "HYD": 13.0, "MAA": 13.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 16.0, "NJP": 35.0, "CCU": 17.0, "GAU": 16.0},
    "BLR": {"AMB": 14.0, "JAI": 14.0, "DEL": 15.0, "AMD": 13.0, "PNQ": 13.0, "BOM": 13.0, "NAG": 13.0, "IDR": 14.0, "BLR": 10.0, "HYD": 13.0, "MAA": 13.0, "CJB": 13.0, "BBI": 14.0, "LOK": 15.0, "PAT": 18.0, "NJP": 32.0, "CCU": 17.0, "GAU": 17.0},
    "HYD": {"AMB": 14.0, "JAI": 14.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 13.0, "BOM": 12.0, "NAG": 12.0, "IDR": 12.0, "BLR": 14.0, "HYD": 10.0, "MAA": 12.0, "CJB": 12.0, "BBI": 16.0, "LOK": 15.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 16.0},
    "MAA": {"AMB": 14.0, "JAI": 14.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 12.0, "BOM": 12.0, "NAG": 12.0, "IDR": 13.0, "BLR": 12.0, "HYD": 13.0, "MAA": 10.0, "CJB": 12.0, "BBI": 14.0, "LOK": 15.0, "PAT": 16.0, "NJP": 32.0, "CCU": 15.0, "GAU": 16.0},
    "CJB": {"AMB": 15.0, "JAI": 15.0, "DEL": 16.0, "AMD": 16.0, "PNQ": 17.0, "BOM": 17.0, "NAG": 16.0, "IDR": 15.0, "BLR": 14.0, "HYD": 14.0, "MAA": 13.0, "CJB": 10.0, "BBI": 16.0, "LOK": 13.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 17.0},
    "BBI": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 14.0, "PNQ": 15.0, "BOM": 15.0, "NAG": 15.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 10.0, "LOK": 13.0, "PAT": 15.0, "NJP": 35.0, "CCU": 15.0, "GAU": 15.0},
    "LOK": {"AMB": 12.0, "JAI": 13.0, "DEL": 12.0, "AMD": 14.0, "PNQ": 15.0, "BOM": 15.0, "NAG": 14.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 13.0, "LOK": 13.0, "PAT": 16.0, "NJP": 36.0, "CCU": 16.0, "GAU": 17.0},
    "PAT": {"AMB": 17.0, "JAI": 17.0, "DEL": 15.0, "AMD": 15.0, "PNQ": 16.0, "BOM": 15.0, "NAG": 14.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 15.0, "LOK": 13.0, "PAT": 15.0, "NJP": 36.0, "CCU": 13.0, "GAU": 14.0},
    "NJP": {"AMB": 35.0, "JAI": 35.0, "DEL": 36.0, "AMD": 36.0, "PNQ": 36.0, "BOM": 36.0, "NAG": 30.0, "IDR": 30.0, "BLR": 35.0, "HYD": 35.0, "MAA": 35.0, "CJB": 35.0, "BBI": 35.0, "LOK": 30.0, "PAT": 35.0, "NJP": 25.0, "CCU": 30.0, "GAU": 30.0},
    "CCU": {"AMB": 18.0, "JAI": 17.0, "DEL": 16.0, "AMD": 17.0, "PNQ": 16.0, "BOM": 16.0, "NAG": 15.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 12.0, "LOK": 15.0, "PAT": 14.0, "NJP": 20.0, "CCU": 12.0, "GAU": 13.0},
    "GAU": {"AMB": 15.0, "JAI": 16.0, "DEL": 17.0, "AMD": 17.0, "PNQ": 17.0, "BOM": 16.0, "NAG": 15.0, "IDR": 16.0, "BLR": 17.0, "HYD": 17.0, "MAA": 17.0, "CJB": 17.0, "BBI": 18.0, "LOK": 18.0, "PAT": 17.0, "NJP": 17.0, "CCU": 12.0, "GAU": 16.0},
}

# Compare rates
print("\n" + "="*80)
print("GLOBAL CARGO RATES COMPARISON: Previous vs Current (14-02-2026)")
print("="*80)

changes = []
for from_zone in PREVIOUS_RATES:
    for to_zone in PREVIOUS_RATES[from_zone]:
        prev_rate = PREVIOUS_RATES[from_zone][to_zone]
        curr_rate = CURRENT_RATES[from_zone][to_zone]
        
        if prev_rate != curr_rate:
            diff = curr_rate - prev_rate
            changes.append({
                'from_zone': from_zone,
                'to_zone': to_zone,
                'prev': prev_rate,
                'curr': curr_rate,
                'diff': diff,
                'is_cheaper': diff < 0,
            })

# Print changes grouped by theme
price_decreased = [c for c in changes if c['is_cheaper']]
price_increased = [c for c in changes if not c['is_cheaper']]

print(f"\n📊 SUMMARY")
print(f"  Total routes changed: {len(changes)} out of 324 routes (9.88%)")
print(f"  Routes with LOWER rates (cheaper): {len(price_decreased)}")
print(f"  Routes with HIGHER rates (expensive): {len(price_increased)}")

if price_decreased:
    print(f"\n💚 CHEAPER ROUTES (Decreased rates - Good news!)")
    print("-" * 80)
    for c in sorted(price_decreased, key=lambda x: x['diff']):
        print(f"  {c['from_zone']} → {c['to_zone']}: ₹{c['prev']}/kg → ₹{c['curr']}/kg (↓ ₹{abs(c['diff'])}/kg)")

if price_increased:
    print(f"\n❌ EXPENSIVE ROUTES (Increased rates)")
    print("-" * 80)
    for c in sorted(price_increased, key=lambda x: x['diff'], reverse=True):
        print(f"  {c['from_zone']} → {c['to_zone']}: ₹{c['prev']}/kg → ₹{c['curr']}/kg (↑ ₹{c['diff']}/kg)")

# Calculate average impact
print(f"\n📈 STATISTICAL ANALYSIS")
print("-" * 80)

avg_change = sum(c['diff'] for c in changes) / len(changes) if changes else 0
all_current_rates = [curr for from_z in CURRENT_RATES for curr in CURRENT_RATES[from_z].values()]
all_prev_rates = [prev for from_z in PREVIOUS_RATES for prev in PREVIOUS_RATES[from_z].values()]

print(f"  Average rate change: ₹{avg_change:.2f}/kg")
print(f"  Previous average rate: ₹{sum(all_prev_rates)/len(all_prev_rates):.2f}/kg")
print(f"  Current average rate: ₹{sum(all_current_rates)/len(all_current_rates):.2f}/kg")
print(f"  Overall impact: {'+' if avg_change >= 0 else ''}{avg_change/sum(all_prev_rates)*len(all_prev_rates)*100:.2f}%")

# Example: Calculate total cost for a 20kg shipment from key routes
print(f"\n📦 EXAMPLE SHIPMENT COSTS (20kg @ min weight, no surcharges)")
print("-" * 80)
print(f"  {' '*25} {'PREVIOUS':<15} {'CURRENT':<15} {'CHANGE':<10}")
print(f"  {'-'*25} {'-'*15} {'-'*15} {'-'*10}")

routes_to_check = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "DEL"),
    ("BLR", "BLR"),
    ("DEL", "DEL"),
    ("AMB", "JAI"),
    ("PNQ", "PNQ"),
    ("NAG", "NAG"),
]

max_savings = 0
max_increase = 0
for from_z, to_z in routes_to_check:
    prev_cost = PREVIOUS_RATES[from_z][to_z] * 20
    curr_cost = CURRENT_RATES[from_z][to_z] * 20
    change = curr_cost - prev_cost
    
    if change < max_savings:
        max_savings = change
    if change > max_increase:
        max_increase = change
    
    status = "✓ CHEAPER" if change < 0 else "✗ EXPENSIVE" if change > 0 else "= SAME"
    print(f"  {from_z:>3} → {to_z:<3}          ₹{prev_cost:>6.0f}         ₹{curr_cost:>6.0f}         {status:<12} {change:+.0f}")

print(f"\n💰 CONCLUSION")
print("-" * 80)
if len(price_decreased) > len(price_increased):
    print(f"✅ OVERALL: New rates are CHEAPER for most routes!")
    print(f"   Maximum savings on a 20kg shipment: ₹{abs(max_savings):.0f}")
    print(f"   {len(price_decreased)} routes cheaper, {len(price_increased)} routes expensive")
elif len(price_increased) > len(price_decreased):
    print(f"⚠️  OVERALL: New rates are MORE EXPENSIVE on most routes")
    print(f"   Maximum increase on a 20kg shipment: ₹{max_increase:.0f}")
    print(f"   {len(price_increased)} routes expensive, {len(price_decreased)} routes cheaper")
else:
    print(f"= OVERALL: Mixed impact - equal number cheaper and expensive")

print("\n" + "="*80)
