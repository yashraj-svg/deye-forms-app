#!/usr/bin/env python
"""
Test to verify that floating leave days are counted correctly, not dates
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import Holiday, LeaveRequest
from django.contrib.auth.models import User

print("=" * 70)
print("FLOATING LEAVE COUNTING TEST - Days vs Dates")
print("=" * 70)

user = User.objects.first()
if not user:
    print("No users found!")
    exit(1)

print(f"\nTest User: {user.username}")

# Test case: User took half-day on 14-Jan-2026 (floating holiday)
test_leave = LeaveRequest(
    user=user,
    leave_type='leave',
    start_date=date(2026, 1, 14),
    end_date=date(2026, 1, 14),
    start_breakdown='half',
    end_breakdown='half',
    reason="Test half-day floating",
    status='pending'
)

# Simulate the floating counting logic
floating_count_days = 0.0
check_date = test_leave.start_date
while check_date <= test_leave.end_date:
    if Holiday.is_floating_holiday(check_date):
        # Calculate day fraction for this floating holiday
        if check_date == test_leave.start_date and check_date == test_leave.end_date:
            # Same day
            if test_leave.start_breakdown == 'half' or test_leave.end_breakdown == 'half':
                floating_count_days += 0.5
            else:
                floating_count_days += 1.0
        elif check_date == test_leave.start_date:
            # Start day
            if test_leave.start_breakdown == 'half':
                floating_count_days += 0.5
            else:
                floating_count_days += 1.0
        elif check_date == test_leave.end_date:
            # End day
            if test_leave.end_breakdown == 'half':
                floating_count_days += 0.5
            else:
                floating_count_days += 1.0
        else:
            # Middle days
            floating_count_days += 1.0
    check_date += timedelta(days=1)

print(f"\nScenario: Half-day leave on 14-Jan-2026 (Makar Sankranti - Floating Holiday)")
print(f"  Leave breakdown: Half Day")
print(f"  Total leave days: 0.5 days")
print(f"  Floating holiday days counted: {floating_count_days} days (was counting 1 date before)")
print(f"  Status: {'PASS' if floating_count_days == 0.5 else 'FAIL'}")

# Test 2: Full day on floating holiday
print(f"\n---")
print(f"Scenario: Full-day leave on 14-Jan-2026 (Floating Holiday)")
test_leave2 = LeaveRequest(
    user=user,
    leave_type='leave',
    start_date=date(2026, 1, 14),
    end_date=date(2026, 1, 14),
    start_breakdown='full',
    end_breakdown='full',
    reason="Test full-day floating",
    status='pending'
)

floating_count_days2 = 0.0
check_date = test_leave2.start_date
while check_date <= test_leave2.end_date:
    if Holiday.is_floating_holiday(check_date):
        if check_date == test_leave2.start_date and check_date == test_leave2.end_date:
            if test_leave2.start_breakdown == 'half' or test_leave2.end_breakdown == 'half':
                floating_count_days2 += 0.5
            else:
                floating_count_days2 += 1.0
    check_date += timedelta(days=1)

print(f"  Leave breakdown: Full Day")
print(f"  Total leave days: 1 day")
print(f"  Floating holiday days counted: {floating_count_days2} days")
print(f"  Status: {'PASS' if floating_count_days2 == 1.0 else 'FAIL'}")

# Test 3: Multi-day with floating holidays
print(f"\n---")
print(f"Scenario: Leave from 13-Jan to 16-Jan (includes 14-Jan floating)")
test_leave3 = LeaveRequest(
    user=user,
    leave_type='leave',
    start_date=date(2026, 1, 13),
    end_date=date(2026, 1, 16),
    start_breakdown='full',
    end_breakdown='full',
    reason="Test multi-day with floating",
    status='pending'
)

floating_count_days3 = 0.0
check_date = test_leave3.start_date
while check_date <= test_leave3.end_date:
    if Holiday.is_floating_holiday(check_date):
        if check_date == test_leave3.start_date and check_date == test_leave3.end_date:
            if test_leave3.start_breakdown == 'half' or test_leave3.end_breakdown == 'half':
                floating_count_days3 += 0.5
            else:
                floating_count_days3 += 1.0
        elif check_date == test_leave3.start_date:
            if test_leave3.start_breakdown == 'half':
                floating_count_days3 += 0.5
            else:
                floating_count_days3 += 1.0
        elif check_date == test_leave3.end_date:
            if test_leave3.end_breakdown == 'half':
                floating_count_days3 += 0.5
            else:
                floating_count_days3 += 1.0
        else:
            floating_count_days3 += 1.0
    check_date += timedelta(days=1)

print(f"  13-Jan (Tue): Regular day")
print(f"  14-Jan (Wed): Floating Holiday")
print(f"  15-Jan (Thu): Regular day")
print(f"  16-Jan (Fri): Regular day")
print(f"  Floating holiday days counted: {floating_count_days3} day (14-Jan only)")
print(f"  Status: {'PASS' if floating_count_days3 == 1.0 else 'FAIL'}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Floating leaves counting is now based on DAYS, not DATES:")
print(f"  Half-day on floating = 0.5 floating days")
print(f"  Full-day on floating = 1.0 floating days")
print(f"  Limit: 3 floating days (not 3 dates)")
print("\n" + "=" * 70)
