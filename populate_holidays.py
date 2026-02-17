#!/usr/bin/env python
"""
Script to populate 2026 Holiday Calendar into database
"""
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import Holiday

# Fixed holidays (cannot request leave on these dates)
fixed_holidays = [
    {'date': date(2026, 1, 1), 'name': "New Year's Day", 'category': 'Optional'},
    {'date': date(2026, 1, 26), 'name': 'Republic Day', 'category': 'National'},
    {'date': date(2026, 3, 2), 'name': 'Holi', 'category': 'Festival'},
    {'date': date(2026, 5, 1), 'name': 'Maharashtra Day / Labor Day / Budha Pournima', 'category': 'Regional'},
    {'date': date(2026, 8, 15), 'name': 'Independence Day', 'category': 'National'},
    {'date': date(2026, 9, 15), 'name': 'Ganesh Chaturthi', 'category': 'Regional'},
    {'date': date(2026, 10, 2), 'name': 'Gandhi Jayanti', 'category': 'National'},
    {'date': date(2026, 10, 19), 'name': 'Navratri', 'category': 'Festival'},
    {'date': date(2026, 10, 20), 'name': 'Dussehra (Vijayadashami)', 'category': 'Festival'},
    {'date': date(2026, 11, 9), 'name': 'Diwali (Deepavali)', 'category': 'Festival'},
    {'date': date(2026, 11, 10), 'name': 'Diwali (Deepavali)', 'category': 'Festival'},
    {'date': date(2026, 11, 11), 'name': 'Diwali (Deepavali)', 'category': 'Festival'},
]

# Floating holidays (employees can choose 3 from this list)
floating_holidays = [
    {'date': date(2026, 1, 14), 'name': 'Makar Sankranti / Magha Bihu / Pongal / Lohari', 'category': 'Festival'},
    {'date': date(2026, 3, 3), 'name': 'Dhulivandan', 'category': 'Festival'},
    {'date': date(2026, 3, 19), 'name': 'Gudi Padwa / Ugadi', 'category': 'Festival'},
    {'date': date(2026, 3, 20), 'name': 'Eid-ul-Fitr / Ramzan', 'category': 'Festival'},
    {'date': date(2026, 3, 31), 'name': 'Mahaveer Jayanti', 'category': 'Festival'},
    {'date': date(2026, 4, 3), 'name': 'Good Friday', 'category': 'Festival'},
    {'date': date(2026, 4, 13), 'name': 'Baishakhi', 'category': 'Festival'},
    {'date': date(2026, 4, 14), 'name': 'Ambedkar Jayanti / Tamil New Year / Vaishadi (Bengal)', 'category': 'Festival'},
    {'date': date(2026, 4, 15), 'name': 'Bahag Bihu (Assam)', 'category': 'Festival'},
    {'date': date(2026, 5, 27), 'name': 'Bakrid / Eid-ul-Adha', 'category': 'Festival'},
    {'date': date(2026, 6, 16), 'name': 'Moharam', 'category': 'Festival'},
    {'date': date(2026, 7, 29), 'name': 'Gurupournima', 'category': 'Festival'},
    {'date': date(2026, 8, 26), 'name': 'Milad-un-Nabi', 'category': 'Festival'},
    {'date': date(2026, 8, 28), 'name': 'Raksha Bandhan', 'category': 'Festival'},
    {'date': date(2026, 9, 4), 'name': 'Janmashtami', 'category': 'Festival'},
    {'date': date(2026, 9, 25), 'name': 'Anant Chaturdashi', 'category': 'Festival'},
    {'date': date(2026, 11, 24), 'name': 'Gurunanak Jayanthi', 'category': 'Festival'},
    {'date': date(2026, 12, 25), 'name': 'Christmas', 'category': 'Festival'},
]

print("Populating Fixed Holidays...")
created_count = 0
for holiday in fixed_holidays:
    obj, created = Holiday.objects.update_or_create(
        date=holiday['date'],
        defaults={
            'name': holiday['name'],
            'category': holiday['category'],
            'is_floating': False,
            'description': ''
        }
    )
    if created:
        created_count += 1
        print(f"✓ Created: {obj}")
    else:
        print(f"✓ Updated: {obj}")

print(f"\nFixed holidays: {created_count} created/updated")

print("\nPopulating Floating Holidays...")
created_count = 0
for holiday in floating_holidays:
    obj, created = Holiday.objects.update_or_create(
        date=holiday['date'],
        defaults={
            'name': holiday['name'],
            'category': holiday['category'],
            'is_floating': True,
            'description': 'Employees can choose this as floating leave (max 3 total)'
        }
    )
    if created:
        created_count += 1
        print(f"✓ Created: {obj}")
    else:
        print(f"✓ Updated: {obj}")

print(f"\nFloating holidays: {created_count} created/updated")

# Display summary
total_holidays = Holiday.objects.count()
fixed_count = Holiday.objects.filter(is_floating=False).count()
floating_count = Holiday.objects.filter(is_floating=True).count()

print(f"\n{'='*60}")
print(f"Holiday Calendar Populated Successfully!")
print(f"{'='*60}")
print(f"Total Holidays: {total_holidays}")
print(f"Fixed Holidays (cannot request leave): {fixed_count}")
print(f"Floating Holidays (choose max 3): {floating_count}")
print(f"{'='*60}")
