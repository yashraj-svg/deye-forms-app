"""
Comprehensive Form Testing Script - Creates 10 entries for each form
Tests: Repairing, Inward, Outward, Service Report
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from django.contrib.auth.models import User
from forms.models import RepairingForm, InwardForm, OutwardForm, ServiceReportForm
from datetime import date, timedelta
import json

# Get or create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@deyeindia.in', 'first_name': 'Test', 'last_name': 'User'}
)

print("=" * 80)
print("COMPREHENSIVE FORM TESTING - 10 ENTRIES PER FORM")
print("=" * 80)

# REPAIRING FORM - 10 ENTRIES
print("\n📝 Testing REPAIRING FORM (10 entries)...")
rep_created = 0
for i in range(1, 11):
    try:
        RepairingForm.objects.create(
            user=user,
            customer_abbrev=f'CUST{i:03d}',
            repairing_object='Inverter' if i % 3 != 0 else 'PCB',
            inverter_id=f'INV-2024-{i:03d}',
            pcb_serial_number=f'PCB-{i:03d}',
            pcb_specification=f'{12 + i*2}V {50 + i*10}A',
            pcb_rating=f'{1000 + i*100}W',
            inverter_spec=f'{5 + i}KW Hybrid',
            inverter_rating=f'{5000 + i*1000}W',
            battery=f'Lithium 48V {100 + i*10}Ah',
            fault_problems={},
            fault_description=f'Fault description for repair {i}',
            fault_location=f'Fault location {i}',
            repair_content=f'Repair work completed for case {i}',
            repaired_by=f'Engineer{i}',
            tested_by=f'Tester{i}',
            repaired_on_date=date.today() - timedelta(days=i),
            remark='Completed',
        )
        rep_created += 1
        print(f"  ✓ Created repairing form {rep_created}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
print(f"✅ Repairing Forms: {rep_created}/10")

# INWARD FORM - 10 ENTRIES  
print("\n📥 Testing INWARD FORM (10 entries)...")
inw_created = 0
for i in range(1, 11):
    try:
        InwardForm.objects.create(
            user=user,
            email=user.email,
            inward_object='Inverter' if i % 3 != 0 else 'PCB',
            customer_abbrev=f'CUST{100+i:03d}',
            customer_name=f'Customer Company {i}',
            inverter_id=f'INV-IN-{i:03d}' if i % 3 != 0 else '',
            battery_id=f'BAT-IN-{i:03d}' if i % 2 == 0 else '',
            pcb_serial_number=f'PCB-IN-{i:03d}' if i % 3 == 0 else '',
            inverter_specs=f'{5+i}KW Hybrid',
            inverter_ratings=f'{5000+i*500}W 48V',
            battery=f'Lithium 48V {100+i*10}Ah' if i % 2 == 0 else '',
            no_of_mppt=2 if i < 5 else 3,
            current_mppt=f'{20+i}A',
            pcb_quantity=1 if i % 3 != 0 else 5,
            received_from_location=f'City{i}',
            received_from_district=f'District{i}',
            received_from_state=f'State{i}',
            pincode=f'{400001+i}',
            received_by=f'Warehouse Team {i}',
            reason='Repair' if i % 2 == 0 else 'Stock',
            transportation_mode='Road' if i % 3 == 0 else 'Rail',
            awb_lr_number=f'AWB{12345+i}',
            accessories=json.dumps(['Charger', 'Manual']),
        )
        inw_created += 1
        print(f"  ✓ Created inward form {inw_created}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
print(f"✅ Inward Forms: {inw_created}/10")

# OUTWARD FORM - 10 ENTRIES
print("\n📤 Testing OUTWARD FORM (10 entries)...")
out_created = 0
for i in range(1, 11):
    try:
        OutwardForm.objects.create(
            user=user,
            outward_object='Inverter' if i % 3 != 0 else 'PCB',
            inverter_id_outward=f'INV-OUT-{i:03d}' if i % 3 != 0 else '',
            inverter_spec=f'{5+i}KW Hybrid',
            inverter_rating=f'{5000+i*500}W',
            battery=f'Lithium 48V {100+i*10}Ah' if i % 2 == 0 else '',
            battery_id=f'BAT-OUT-{i:03d}' if i % 2 == 0 else '',
            sent_to_company=f'Company {i} Ltd',
            sent_to_address=f'{i*100} Street {i}',
            sent_to_district=f'District{i}',
            sent_to_state=f'State{i}',
            pincode=f'{500001+i}',
            sent_by=f'Sender{i}',
            approved_by=f'Manager{i}',
            company_abbrev=f'CO{i}',
            control_card_changed='Yes' if i % 2 == 0 else 'No',
            new_serial_number=f'NEW-{i:03d}' if i % 2 == 0 else '',
            inverter_id_inward=f'INV-IN-{i:03d}',
            inverter_replaced='Yes' if i % 3 == 0 else 'No',
            delivered_through='Courier' if i % 2 == 0 else 'Hand Delivery',
            awb_number=f'AWB-OUT-{i:03d}',
            accessories=json.dumps(['Charger']),
        )
        out_created += 1
        print(f"  ✓ Created outward form {out_created}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
print(f"✅ Outward Forms: {out_created}/10")

# SERVICE REPORT FORM - 10 ENTRIES
print("\n🛠️  Testing SERVICE REPORT FORM (10 entries)...")
svc_created = 0
for i in range(1, 11):
    try:
        ServiceReportForm.objects.create(
            user=user,
            engineer_first_name=f'Engineer{i}',
            engineer_last_name=f'Last{i}',
            customer_first_name=f'Customer{i}',
            customer_last_name=f'Name{i}',
            product_type='Hybrid Inverter' if i % 2 == 0 else 'Off-Grid Inverter',
            serial_number=f'SER-2024-{i:03d}',
            date_of_service=date.today() - timedelta(days=i),
            inverter_capacity=f'{5+i}KW',
            pv_capacity_kw=float(6+i),
            no_of_mppt=2 if i < 5 else 3,
            address_street=f'{i*100} Main Street',
            address_city=f'City{i}',
            address_state=f'State{i}',
            address_zip=f'{600001+i}',
            phone_number=f'98765432{i:02d}',
            email=f'customer{i}@example.com',
            lcd_version=f'v2.{i}',
            mcu_version=f'v3.{i}',
            battery_type='Lithium' if i % 2 == 0 else 'Tubular',
            battery_make='Deye' if i % 2 == 0 else 'Exide',
            battery_voltage='48V',
            protocol='CAN' if i % 2 == 0 else 'RS485',
            physical_observation=f'Observation {i}',
            actual_work_done=f'Work done for service {i}',
            cause_of_failure=f'Cause {i}',
            ac_cable_size='10mm²',
            conclusion='Working OK',
            customer_ratings='5 Stars',
            suggestions=f'Suggestion {i}',
            pv_data=json.dumps([
                {'voltage': '400', 'current': '12', 'earthing': 'OK', 'panel': '72 Cell', 'observation': 'Good'}
            ]),
            ac_data=json.dumps({
                'R-N': {'voltage': '230', 'current': '10', 'earthing': 'OK'}
            }),
        )
        svc_created += 1
        print(f"  ✓ Created service report {svc_created}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
print(f"✅ Service Reports: {svc_created}/10")

# SUMMARY
print("\n" + "=" * 80)
print("TESTING SUMMARY")
print("=" * 80)
print(f"📝 Repairing Forms: {rep_created}/10")
print(f"📥 Inward Forms: {inw_created}/10")
print(f"📤 Outward Forms: {out_created}/10")
print(f"🛠️  Service Reports: {svc_created}/10")
print(f"\n📊 Total: {rep_created + inw_created + out_created + svc_created}/40 forms created")

# DATABASE COUNTS
print("\n" + "=" * 80)
print("DATABASE VERIFICATION")
print("=" * 80)
print(f"📝 Total Repairing Forms in DB: {RepairingForm.objects.count()}")
print(f"📥 Total Inward Forms in DB: {InwardForm.objects.count()}")
print(f"📤 Total Outward Forms in DB: {OutwardForm.objects.count()}")
print(f"🛠️  Total Service Reports in DB: {ServiceReportForm.objects.count()}")
print("\n✅ ALL TESTING COMPLETE!")
print("=" * 80)
