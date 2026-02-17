
from datetime import date, timedelta
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

# Model for future extensibility (not strictly needed for dynamic aggregation, but useful if you want to persist requests)
class RequiredStock(models.Model):
    serial_number = models.CharField(max_length=100, db_index=True)
    component_type = models.CharField(max_length=100)
    quantity_required = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'required_stock'
        verbose_name = 'Required Stock'
        verbose_name_plural = 'Required Stock'
        unique_together = ('serial_number', 'component_type')

    def __str__(self):
        return f"{self.serial_number} - {self.component_type} (Need: {self.quantity_required})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=50, blank=True, help_text="Employee ID/Number")
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, help_text="Profile Photo")
    date_of_birth = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True, help_text="Date of Joining")
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=255, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members', help_text="Manager of this user")
    location = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=100, blank=True, help_text="Region/Territory")
    is_active = models.BooleanField(default=True, help_text="Is employee currently active")
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_team_members(self):
        """Get all users who report to this user"""
        return User.objects.filter(profile__manager=self.user)


class UpcomingEvent(models.Model):
    title = models.CharField(max_length=200)
    event_date = models.DateField()
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date', 'title']

    def __str__(self):
        date_text = self.event_date.strftime('%Y-%m-%d') if self.event_date else 'date?'
        return f"{self.title} ({date_text})"


class RepairingForm(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, help_text="User who filled the form")
    # PCB Details (for PCB object)
    pcb_serial_number = models.CharField(max_length=255, blank=True, null=True, help_text="PCB Serial Number")
    pcb_specification = models.CharField(max_length=255, blank=True, null=True, help_text="PCB Specification")
    pcb_rating = models.CharField(max_length=255, blank=True, null=True, help_text="PCB Rating")
    customer_abbrev = models.CharField(max_length=255)
    case_number = models.CharField(
        max_length=255,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message='Case Number must be exactly 8 digits.'
            )
        ]
    )
    repairing_object = models.CharField(max_length=255)
    inverter_id = models.TextField(blank=True)
    inverter_spec = models.CharField(max_length=255)
    inverter_rating = models.CharField(max_length=255, blank=True)
    battery = models.CharField(max_length=255, blank=True)

    # Fault details
    fault_problems = models.JSONField(default=dict)
    fault_description = models.TextField()
    pcba_serial = models.CharField(max_length=255, blank=True)
    fault_location = models.TextField()

    # Repair work
    repair_content = models.TextField()
    repaired_by = models.CharField(max_length=255)
    tested_by = models.CharField(max_length=255)
    repaired_on_date = models.DateField()
    repaired_location = models.CharField(max_length=255, blank=True, default='')

    # Status
    remark = models.CharField(max_length=255, blank=True, default='')
    pending_component = models.CharField(max_length=255, blank=True)

    # Images
    image_before = models.CharField(max_length=500, blank=True)
    image_after = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, help_text="Form filled date/time")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Repair {self.case_number} - {self.customer_abbrev}"


class InwardForm(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, help_text="User who filled the form")
    inward_object = models.CharField(max_length=50, blank=True, null=True, help_text="Type of object for inward (Inverter, Battery, PCB)")
    # Accessories (optional, only for Inverter)
    ACCESSORY_CHOICES = [
        ('data_logger', 'Data Logger'),
        ('stand', 'Stand'),
    ]
    accessories = models.JSONField(blank=True, null=True, default=list, help_text="Accessories selected (Data Logger, Stand)")
    email = models.EmailField(blank=True, null=True)
    received_by = models.CharField(max_length=255)
    customer_abbrev = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)

    # Location details
    received_from_location = models.CharField(max_length=255, blank=True)
    received_from_district = models.CharField(max_length=255, blank=True)
    received_from_state = models.CharField(max_length=255, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    # Inverter / Battery Details
    inverter_id = models.CharField(max_length=255)
    battery_id = models.CharField(max_length=255, blank=True, null=True, help_text="Unique Battery Serial Number")
    inverter_specs = models.CharField(max_length=255)
    inverter_ratings = models.CharField(max_length=255, blank=True)
    battery = models.CharField(max_length=255, blank=True)
    no_of_mppt = models.CharField(max_length=10, blank=True)
    current_mppt = models.CharField(max_length=10, blank=True)

    # PCB Details (for PCB object)
    pcb_serial_number = models.CharField(max_length=255, blank=True, null=True, help_text="PCB Serial Number")
    pcb_quantity = models.PositiveIntegerField(blank=True, null=True, help_text="No of Quantity")

    # Service Details
    case_handled_by = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=255)
    transportation_mode = models.CharField(max_length=255, blank=True)
    awb_lr_number = models.CharField(max_length=255, blank=True)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, help_text="Form filled date/time")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inward {self.customer_name} - {self.email}"


class OutwardForm(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, help_text="User who filled the form")
    outward_object = models.CharField(max_length=50, blank=True, null=True, help_text="Type of object for outward (Inverter, Battery, PCB)")
    sent_by = models.CharField(max_length=255)
    approved_by = models.CharField(max_length=255)
    company_abbrev = models.CharField(max_length=255)

    # Destination details
    sent_to_company = models.CharField(max_length=255)
    sent_to_address = models.TextField()
    sent_to_district = models.CharField(max_length=255)
    sent_to_state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)



    # Accessories (optional, only for Inverter)
    accessories = models.JSONField(blank=True, null=True, default=list, help_text="Accessories selected (Data Logger, Stand)")

    # Control Card Changed fields
    control_card_changed = models.CharField(max_length=10, blank=True, help_text="Was control card changed? (Yes/No)")
    new_serial_number = models.CharField(max_length=100, blank=True, help_text="New serial number if control card changed")

    # Inverter details
    inverter_id_outward = models.CharField(max_length=255)
    inverter_spec = models.CharField(max_length=255)
    inverter_rating = models.CharField(max_length=255, blank=True)
    battery = models.CharField(max_length=255, blank=True)
    battery_id = models.CharField(max_length=255, blank=True, null=True, help_text="Unique Battery Serial Number")

    # Replacement status
    inverter_replaced = models.CharField(max_length=10)
    replacement_type = models.CharField(max_length=255, blank=True)
    inverter_id_inward = models.CharField(max_length=255, blank=True)

    # Delivery
    delivered_through = models.CharField(max_length=255)
    courier_name = models.CharField(max_length=100, blank=True, null=True, help_text="Courier name for delivery")
    awb_number = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True, help_text="Form filled date/time")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Outward {self.inverter_id_outward} - {self.sent_to_company}"


class ServiceReportForm(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, help_text="User who filled the form")
    # Contact Information
    contact_no = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    # Engineer Details
    engineer_first_name = models.CharField(max_length=255)
    engineer_last_name = models.CharField(max_length=255)

    # Customer Details
    customer_first_name = models.CharField(max_length=255)
    customer_last_name = models.CharField(max_length=255)
    date_of_service = models.DateField(blank=True, null=True)

    # Address
    address_street = models.TextField()
    address_city = models.CharField(max_length=255, blank=True)
    address_state = models.CharField(max_length=255, blank=True)
    address_zip = models.CharField(max_length=10, blank=True)

    # Product & Device Information
    product_type = models.CharField(max_length=255)
    inverter_capacity = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    lcd_version = models.CharField(max_length=255)
    mcu_version = models.CharField(max_length=255)
    pv_capacity_kw = models.FloatField()
    no_of_mppt = models.IntegerField()

    # Component Checks (Checkboxes)
    dc_spd = models.BooleanField(default=False)
    dc_switch = models.BooleanField(default=False)
    dc_fuse = models.BooleanField(default=False)
    ac_spd = models.BooleanField(default=False)
    ac_switch = models.BooleanField(default=False)
    ac_fuse = models.BooleanField(default=False)
    earthing_panel = models.BooleanField(default=False)
    earthing_inverter = models.BooleanField(default=False)
    earthing_ac_neutral = models.BooleanField(default=False)
    ac_neutral_earth_voltage = models.CharField(max_length=100, blank=True)
    ac_cable_size = models.CharField(max_length=100, blank=True)

    # Physical Observation
    physical_observation = models.TextField()

    # PV Data (as JSON array)
    pv_data = models.JSONField(default=list)

    # AC Data (as JSON object)
    ac_data = models.JSONField(default=dict)

    # Repair Details
    repair_inverter = models.TextField(blank=True)
    repair_dust = models.TextField(blank=True)
    repair_cabling = models.TextField(blank=True)
    repair_other = models.TextField(blank=True)

    # Work Details
    actual_work_done = models.TextField()
    cause_of_failure = models.TextField()

    # Battery Information
    battery_type = models.CharField(max_length=255, blank=True)
    battery_make = models.CharField(max_length=255, blank=True)
    battery_voltage = models.CharField(max_length=100, blank=True)
    battery_protection = models.CharField(max_length=255, blank=True)
    no_of_battery = models.IntegerField(blank=True, null=True)
    battery_bms_make = models.CharField(max_length=255, blank=True)
    battery_bms_model = models.CharField(max_length=255, blank=True)
    battery_bms_ratings = models.CharField(max_length=255, blank=True)

    # Final Assessment
    protocol = models.TextField()
    conclusion = models.TextField()
    customer_ratings = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)

    # Signatures (stored as base64 data URLs)
    engineer_signature_data = models.TextField(blank=True)
    customer_signature_data = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Service Report {self.engineer_first_name} {self.engineer_last_name}"


class LeaveRequest(models.Model):
    LEAVE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    LEAVE_TYPE_CHOICES = [
        ('leave', 'Leave'),
        ('wfh', 'Work From Home'),
    ]

    DAY_PORTION_CHOICES = [
        ('full', 'Full Day'),
        ('half', 'Half Day'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    start_breakdown = models.CharField(max_length=10, choices=DAY_PORTION_CHOICES, default='full')
    end_breakdown = models.CharField(max_length=10, choices=DAY_PORTION_CHOICES, default='full')
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=LEAVE_STATUS_CHOICES, default='pending')
    total_days = models.FloatField(default=0.0)
    applied_at = models.DateTimeField(auto_now_add=True)
    status_changed_at = models.DateTimeField(blank=True, null=True)
    status_changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_leaves')

    def compute_total_days(self):
        """Compute total days excluding Sundays and respecting half-day boundaries."""
        def _coerce(d):
            if isinstance(d, str):
                try:
                    return date.fromisoformat(d)
                except ValueError:
                    return None
            return d

        start = _coerce(self.start_date)
        end = _coerce(self.end_date)
        if not start or not end:
            return 0.0

        if start > end:
            return 0.0
        
        # Special case: Same day leave
        if start == end:
            if start.weekday() == 6:  # Sunday
                return 0.0
            # Same day: both half days = 0.5 days, otherwise count based on breakdown
            if self.start_breakdown == 'half' and self.end_breakdown == 'half':
                return 0.5
            elif self.start_breakdown == 'half' or self.end_breakdown == 'half':
                return 0.5
            else:  # Both full days
                return 1.0
        
        # Count days excluding Sundays
        days = 0.0
        current = start
        while current <= end:
            if current.weekday() != 6:  # 6 = Sunday
                days += 1.0
            current += timedelta(days=1)

        # Apply half-day adjustments only if the boundary day is not Sunday
        if start.weekday() != 6 and self.start_breakdown == 'half':
            days -= 0.5
        if end.weekday() != 6 and self.end_breakdown == 'half':
            days -= 0.5

        return max(days, 0.0)

    def save(self, *args, **kwargs):
        self.total_days = self.compute_total_days()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.status})"


# -----------------------------
# Freight Calculator Models
# -----------------------------

class PincodeData(models.Model):
    """Master pincode data for all carriers"""
    pincode = models.CharField(max_length=6, primary_key=True, db_index=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    
    # Rahul Delhivery / Global Courier Cargo
    global_cargo_region = models.CharField(max_length=10, blank=True, null=True)
    is_oda = models.BooleanField(null=True, blank=True)  # TRUE=ODA, FALSE=non-ODA, NULL=not deliverable
    deliverable = models.BooleanField(default=True)
    
    # Safexpress
    safexpress_is_oda = models.BooleanField(null=True, blank=True)  # NULL=not in whitelist
    
    # Bigship
    bigship_is_oda = models.BooleanField(null=True, blank=True)  # TRUE=ODA, FALSE/NULL=non-ODA
    
    # Bluedart
    bluedart_region = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        db_table = 'freight_pincode_data'
        verbose_name = 'Pincode Data'
        verbose_name_plural = 'Pincode Data'
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return f"{self.pincode} - {self.city or 'Unknown'}, {self.state or 'Unknown'}"


# -----------------------------
# Stock Inventory Models
# -----------------------------


class StockItem(models.Model):
    """Stock inventory for components and parts"""
    pcba_sn_old = models.CharField(max_length=100, blank=True, null=True, verbose_name="PCBA SN (old)")
    pcba_sn_new = models.CharField(max_length=100, db_index=True, verbose_name="PCBA SN (new)", blank=True, null=True)
    component_type = models.CharField(max_length=255, blank=True, null=True)
    specification = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remark = models.TextField(blank=True, null=True)
    year = models.IntegerField(default=2025, db_index=True, help_text="Year of stock entry")
    shipment_date = models.DateField(null=True, blank=True, help_text="Date of shipment received")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_items'
        verbose_name = 'Stock Item'
        verbose_name_plural = 'Stock Items'
        ordering = ['-shipment_date', '-year', 'component_type', 'pcba_sn_new']
        indexes = [
            models.Index(fields=['year', 'component_type']),
            models.Index(fields=['pcba_sn_new']),
            models.Index(fields=['shipment_date']),
        ]
    
    def __str__(self):
        return f"{self.pcba_sn_new} - {self.component_type or 'N/A'} ({self.year}) - {self.shipment_date}"


class StockRequisition(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, help_text="User who filled the form")
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('dispatched', 'Dispatched'),
    ]
    
    serial_number = models.CharField(max_length=100, db_index=True)
    component_type = models.CharField(max_length=100)
    description = models.TextField()
    manager_name = models.CharField(max_length=200)
    quantity_required = models.IntegerField()
    approved_quantity = models.IntegerField(null=True, blank=True, help_text="Quantity approved to send by stock manager")
    required_to = models.CharField(max_length=100)  # Abbreviation like "DXYZ", "DKOL", etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    approval_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'stock_requisitions'
        verbose_name = 'Stock Requisition'
        verbose_name_plural = 'Stock Requisitions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Req: {self.serial_number} - {self.component_type} ({self.quantity_required}) - {self.status.upper()}"


class DispatchedStock(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, help_text="User who filled the form")
    requisition = models.ForeignKey(StockRequisition, on_delete=models.CASCADE, related_name='dispatches')
    serial_number = models.CharField(max_length=100, db_index=True)
    component_type = models.CharField(max_length=100)
    quantity_dispatched = models.IntegerField()
    engineer_name = models.CharField(max_length=200)
    dispatch_location = models.CharField(max_length=100)
    dispatch_date = models.DateField()
    courier_name = models.CharField(max_length=100)
    tracking_number = models.CharField(max_length=100)
    dispatch_remarks = models.TextField(blank=True, null=True)
    dispatched_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dispatched_stock'
        verbose_name = 'Dispatched Stock'
        verbose_name_plural = 'Dispatched Stock'
        ordering = ['-dispatch_date', '-created_at']
    
    def __str__(self):
        return f"Dispatch: {self.serial_number} - {self.component_type} ({self.quantity_dispatched}) to {self.dispatch_location}"


class Holiday(models.Model):
    """
    Holiday model to store 2026 holiday calendar
    Fixed holidays: cannot request leave on these dates
    Floating holidays: employees can choose 3 from the available pool
    """
    CATEGORY_CHOICES = [
        ('National', 'National Holiday'),
        ('Festival', 'Festival'),
        ('Regional', 'Regional Holiday'),
        ('Optional', 'Optional Holiday'),
    ]

    date = models.DateField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_floating = models.BooleanField(default=False, help_text="True if employees can choose this as floating holiday (max 3)")
    description = models.TextField(blank=True, help_text="Additional description or region-specific info")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'holidays'
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['is_floating']),
        ]

    def __str__(self):
        holiday_type = "Floating" if self.is_floating else "Fixed"
        return f"{self.date.strftime('%d-%b-%Y')} - {self.name} ({holiday_type})"
    
    @classmethod
    def get_fixed_holidays(cls):
        """Get all fixed holidays"""
        return cls.objects.filter(is_floating=False).order_by('date')
    
    @classmethod
    def get_floating_holidays(cls):
        """Get all floating holidays"""
        return cls.objects.filter(is_floating=True).order_by('date')
    
    @classmethod
    def is_holiday(cls, check_date):
        """Check if a date is a holiday"""
        return cls.objects.filter(date=check_date).exists()
    
    @classmethod
    def is_fixed_holiday(cls, check_date):
        """Check if a date is a fixed holiday"""
        return cls.objects.filter(date=check_date, is_floating=False).exists()
    
    @classmethod
    def is_floating_holiday(cls, check_date):
        """Check if a date is a floating holiday"""
        return cls.objects.filter(date=check_date, is_floating=True).exists()


class CheckInOut(models.Model):
    """
    Employee check-in/check-out tracking with location data.
    Stores exact timestamps and GPS coordinates for attendance monitoring.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='checkins',
        help_text="Employee who checked in"
    )
    date = models.DateField(
        auto_now_add=True,
        help_text="Date of check-in"
    )
    
    # Check-in data
    check_in_time = models.DateTimeField(
        help_text="Exact timestamp when employee checked in"
    )
    check_in_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="GPS latitude at check-in"
    )
    check_in_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="GPS longitude at check-in"
    )
    check_in_location = models.CharField(
        max_length=255,
        help_text="Address/location name at check-in"
    )
    
    # Check-out data
    check_out_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Exact timestamp when employee checked out"
    )
    check_out_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="GPS latitude at check-out"
    )
    check_out_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="GPS longitude at check-out"
    )
    check_out_location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Address/location name at check-out"
    )
    
    # Duration calculation
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total hours worked (automatically calculated)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employee_checkin'
        ordering = ['-date', '-check_in_time']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
        verbose_name = 'Check-In/Check-Out'
        verbose_name_plural = 'Check-Ins/Check-Outs'
    
    def __str__(self):
        status = "Checked In" if self.is_checked_in() else "Checked Out"
        return f"{self.user.get_full_name() or self.user.username} - {self.date} ({status})"
    
    def is_checked_in(self):
        """Check if user is currently checked in (no check-out time)"""
        return self.check_out_time is None
    
    def calculate_duration(self):
        """Calculate duration between check-in and check-out in hours"""
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            hours = delta.total_seconds() / 3600
            self.duration_hours = round(hours, 2)
        return self.duration_hours
    
    @classmethod
    def get_today_checkin(cls, user):
        """Get today's check-in record for a user"""
        from django.utils import timezone
        today = timezone.now().date()
        try:
            return cls.objects.filter(user=user, date=today).first()
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_active_checkin(cls, user):
        """Get currently active (not checked out) check-in for a user"""
        return cls.objects.filter(user=user, check_out_time__isnull=True).first()


class LocationTracking(models.Model):
    """
    Model to track hourly location pings for employees during work hours.
    Stores location every hour while checked in, tracks coverage gaps.
    Data retained for 4 months only.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_pings')
    checkin = models.ForeignKey(CheckInOut, on_delete=models.CASCADE, related_name='location_pings', 
                                null=True, blank=True, help_text="Associated check-in session")
    
    # Timestamp
    ping_time = models.DateTimeField(auto_now_add=True, help_text="When location was captured")
    
    # Location data
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                   help_text="GPS Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                    help_text="GPS Longitude")
    location_address = models.TextField(blank=True, help_text="Reverse geocoded address")
    
    # Tracking metadata
    ping_type = models.CharField(max_length=20, choices=[
        ('checkin', 'Check-In'),
        ('hourly', 'Hourly Ping'),
        ('checkout', 'Check-Out'),
        ('recovery', 'Coverage Recovery'),
    ], default='hourly')
    
    is_location_available = models.BooleanField(default=True, 
                                                help_text="Was location available at ping time?")
    coverage_gap_seconds = models.IntegerField(default=0, 
                                               help_text="Seconds without location before this ping")
    
    # Browser/Device info
    accuracy = models.FloatField(null=True, blank=True, help_text="GPS accuracy in meters")
    device_info = models.CharField(max_length=200, blank=True, help_text="Browser/Device details")
    
    class Meta:
        db_table = 'employee_location_tracking'
        ordering = ['-ping_time']
        indexes = [
            models.Index(fields=['user', 'ping_time']),
            models.Index(fields=['checkin', 'ping_time']),
            models.Index(fields=['ping_time']),  # For cleanup queries
        ]
        verbose_name = 'Location Tracking'
        verbose_name_plural = 'Location Tracking Records'
    
    def __str__(self):
        status = "📍" if self.is_location_available else "❌"
        return f"{status} {self.user.username} - {self.ping_type} at {self.ping_time.strftime('%I:%M %p')}"
    
    def get_maps_url(self):
        """Generate Google Maps URL for this location"""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return None
    
    @classmethod
    def cleanup_old_records(cls):
        """Delete records older than 4 months"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=120)  # 4 months
        deleted_count = cls.objects.filter(ping_time__lt=cutoff_date).delete()[0]
        return deleted_count
    
    @classmethod
    def get_user_travel_history(cls, user, days=30):
        """Get user's location tracking history for specified days"""
        from django.utils import timezone
        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=days)
        return cls.objects.filter(user=user, ping_time__gte=start_date).select_related('checkin')
    
    @classmethod
    def record_ping(cls, user, checkin, ping_type='hourly', latitude=None, longitude=None, 
                   location_address='', accuracy=None, device_info='', coverage_gap_seconds=0):
        """Create a new location ping record"""
        is_available = latitude is not None and longitude is not None
        
        return cls.objects.create(
            user=user,
            checkin=checkin,
            ping_type=ping_type,
            latitude=latitude,
            longitude=longitude,
            location_address=location_address,
            is_location_available=is_available,
            accuracy=accuracy,
            device_info=device_info,
            coverage_gap_seconds=coverage_gap_seconds
        )
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        if not all([lat1, lon1, lat2, lon2]):
            return 0.0
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Earth radius in kilometers
        radius = 6371.0
        distance = radius * c
        
        return round(distance, 2)
    
    @classmethod
    def get_daily_locations(cls, user, date):
        """Get all location pings for a specific day"""
        from django.utils import timezone
        from datetime import datetime, time
        
        # Create date range for the day
        start_datetime = timezone.make_aware(datetime.combine(date, time.min))
        end_datetime = timezone.make_aware(datetime.combine(date, time.max))
        
        return cls.objects.filter(
            user=user,
            ping_time__gte=start_datetime,
            ping_time__lte=end_datetime,
            is_location_available=True
        ).order_by('ping_time')
    
    @classmethod
    def calculate_daily_distance(cls, user, date):
        """Calculate total distance travelled in a day"""
        locations = cls.get_daily_locations(user, date)
        
        if locations.count() < 2:
            return 0.0
        
        total_distance = 0.0
        prev_location = None
        
        for location in locations:
            if prev_location:
                distance = cls.calculate_distance(
                    prev_location.latitude, prev_location.longitude,
                    location.latitude, location.longitude
                )
                total_distance += distance
            prev_location = location
        
        return round(total_distance, 2)


class DailyTravelSummary(models.Model):
    """
    Day-wise summary of employee travel with total distance.
    Automatically calculated from LocationTracking records.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_travel_summaries')
    date = models.DateField(help_text="Date of travel")
    
    # Summary data
    total_distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                           help_text="Total distance travelled in kilometers")
    location_count = models.IntegerField(default=0, help_text="Number of location pings recorded")
    
    # Time data
    first_ping_time = models.DateTimeField(null=True, blank=True, help_text="Check-in time")
    last_ping_time = models.DateTimeField(null=True, blank=True, help_text="Check-out time")
    work_duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                              help_text="Total work hours")
    
    # Location data for quick access
    start_location = models.TextField(blank=True, help_text="Check-in location address")
    end_location = models.TextField(blank=True, help_text="Check-out location address")
    
    # Reference to check-in session
    checkin = models.ForeignKey(CheckInOut, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='travel_summary')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_travel_summary'
        unique_together = ('user', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
        verbose_name = 'Daily Travel Summary'
        verbose_name_plural = 'Daily Travel Summaries'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.date} ({self.total_distance_km} km)"
    
    @classmethod
    def generate_summary(cls, user, date):
        """Generate or update daily travel summary for a specific date"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all locations for the day
        locations = LocationTracking.get_daily_locations(user, date)
        location_count = locations.count()
        
        if location_count == 0:
            # No data for this day
            return None
        
        # Calculate total distance
        total_distance = LocationTracking.calculate_daily_distance(user, date)
        
        # Get first and last ping
        first_ping = locations.first()
        last_ping = locations.last()
        
        # Calculate work duration
        work_duration = None
        if first_ping and last_ping and first_ping != last_ping:
            duration_seconds = (last_ping.ping_time - first_ping.ping_time).total_seconds()
            work_duration = round(duration_seconds / 3600, 2)
        
        # Get checkin session
        checkin = CheckInOut.objects.filter(user=user, date=date).first()
        
        # Create or update summary
        summary, created = cls.objects.update_or_create(
            user=user,
            date=date,
            defaults={
                'total_distance_km': total_distance,
                'location_count': location_count,
                'first_ping_time': first_ping.ping_time,
                'last_ping_time': last_ping.ping_time,
                'work_duration_hours': work_duration,
                'start_location': first_ping.location_address,
                'end_location': last_ping.location_address,
                'checkin': checkin,
            }
        )
        
        return summary
    
    def get_all_locations(self):
        """Get all location pings for this day"""
        return LocationTracking.get_daily_locations(self.user, self.date)
    
    def get_maps_route_url(self):
        """Generate Google Maps URL showing the entire day's route"""
        locations = self.get_all_locations()
        
        if locations.count() < 2:
            # Single location - just show that point
            if locations.count() == 1:
                loc = locations.first()
                return f"https://www.google.com/maps?q={loc.latitude},{loc.longitude}"
            return None
        
        # Multiple locations - create route with waypoints
        coords = [f"{loc.latitude},{loc.longitude}" for loc in locations]
        
        # Start and end
        origin = coords[0]
        destination = coords[-1]
        
        # Middle waypoints (Google Maps supports up to 25 waypoints)
        waypoints = "|".join(coords[1:-1][:25]) if len(coords) > 2 else ""
        
        if waypoints:
            return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints}&travelmode=driving"
        else:
            return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"
