"""
Find invoices marked as ODA in December billing but NOT ODA in database
"""
import csv
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import PincodeData

csv_path = r"c:\Users\Yashraj\Desktop\Deye Web App Project\Global Cargo Bill - Dec Month - Sheet1.csv"

print("=" * 120)
print("CHECKING ODA MISMATCHES: Bills marked ODA but pincode is NOT ODA in database")
print("=" * 120)

bills = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            bills.append({
                'sr': row['Sr No'],
                'date': row['Date'],
                'awb': row['AWB No'],
                'invoice': row['Invoice Value'],
                'from_pin': row['From Location'],
                'to_pin': row['To Location'],
                'destination': row['Destination'],
                'weight': float(row['Weight (kg)']),
                'mode': row['Mode'],
                'amount': float(row['Amount (Rs)']),
            })
        except (ValueError, KeyError):
            continue

# Check for mismatches
mismatches = []

for bill in bills:
    if bill['mode'] == 'ODA' and bill['to_pin'] and bill['to_pin'] != '#N/A':
        # Check database
        db_rec = PincodeData.objects.filter(pincode=bill['to_pin']).first()
        
        if db_rec:
            if db_rec.is_oda is False:
                mismatches.append({
                    'bill': bill,
                    'db_status': 'NON-ODA',
                    'city': db_rec.city,
                    'state': db_rec.state,
                })
            elif db_rec.is_oda is None:
                mismatches.append({
                    'bill': bill,
                    'db_status': 'UNKNOWN',
                    'city': db_rec.city,
                    'state': db_rec.state,
                })
        else:
            mismatches.append({
                'bill': bill,
                'db_status': 'NOT IN DATABASE',
                'city': 'Unknown',
                'state': 'Unknown',
            })

if mismatches:
    print(f"\nFound {len(mismatches)} invoices marked as ODA but NOT ODA in database:")
    print("-" * 120)
    print(f"{'Sr#':<5} {'AWB No':<18} {'Date':<12} {'To Pin':<8} {'Destination':<20} {'DB Status':<15} {'Amount':<10}")
    print("-" * 120)
    
    for m in mismatches:
        b = m['bill']
        print(f"{b['sr']:<5} {b['awb']:<18} {b['date']:<12} {b['to_pin']:<8} {b['destination']:<20} {m['db_status']:<15} Rs.{b['amount']:<8.0f}")
    
    print("\n" + "=" * 120)
    print("DETAILED BREAKDOWN:")
    print("=" * 120)
    
    for m in mismatches:
        b = m['bill']
        print(f"\nInvoice #{b['sr']} - AWB: {b['awb']}")
        print(f"  Date: {b['date']}")
        print(f"  From: {b['from_pin']} → To: {b['to_pin']} ({b['destination']})")
        print(f"  City/State: {m['city']}, {m['state']}")
        print(f"  Weight: {b['weight']}kg, Amount: Rs.{b['amount']}")
        print(f"  Bill Mode: ODA")
        print(f"  Database Status: {m['db_status']}")
        print(f"  *** MISMATCH: Billed as ODA but database says {m['db_status']} ***")
else:
    print("\nNo mismatches found - All ODA bills match database ODA status!")

# Also check reverse: Database says ODA but bill shows SFC
print("\n\n" + "=" * 120)
print("REVERSE CHECK: Database marked ODA but billed as SFC (non-ODA)")
print("=" * 120)

reverse_mismatches = []

for bill in bills:
    if bill['mode'] == 'SFC' and bill['to_pin'] and bill['to_pin'] != '#N/A':
        db_rec = PincodeData.objects.filter(pincode=bill['to_pin']).first()
        
        if db_rec and db_rec.is_oda is True:
            reverse_mismatches.append({
                'bill': bill,
                'city': db_rec.city,
                'state': db_rec.state,
            })

if reverse_mismatches:
    print(f"\nFound {len(reverse_mismatches)} invoices billed as SFC but database says ODA:")
    print("-" * 120)
    print(f"{'Sr#':<5} {'AWB No':<18} {'Date':<12} {'To Pin':<8} {'Destination':<20} {'Amount':<10}")
    print("-" * 120)
    
    for m in reverse_mismatches:
        b = m['bill']
        print(f"{b['sr']:<5} {b['awb']:<18} {b['date']:<12} {b['to_pin']:<8} {b['destination']:<20} Rs.{b['amount']:<8.0f}")
else:
    print("\nNo reverse mismatches found!")

print("\n" + "=" * 120)
print("SUMMARY:")
print("=" * 120)
print(f"Total bills checked: {len(bills)}")
print(f"Bills marked ODA in invoice: {sum(1 for b in bills if b['mode'] == 'ODA')}")
print(f"Mismatches (billed ODA, database says NOT ODA): {len(mismatches)}")
print(f"Reverse mismatches (billed SFC, database says ODA): {len(reverse_mismatches)}")
print("=" * 120)
