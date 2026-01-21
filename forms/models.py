from datetime import date, timedelta
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members', help_text="Manager of this user")
    location = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=255, blank=True)
    
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Repair {self.case_number} - {self.customer_abbrev}"


class InwardForm(models.Model):
    email = models.EmailField()
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
    inverter_specs = models.CharField(max_length=255)
    inverter_ratings = models.CharField(max_length=255, blank=True)
    battery = models.CharField(max_length=255, blank=True)
    no_of_mppt = models.CharField(max_length=10, blank=True)
    current_mppt = models.CharField(max_length=10, blank=True)

    # Service Details
    case_handled_by = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=255)
    transportation_mode = models.CharField(max_length=255, blank=True)
    awb_lr_number = models.CharField(max_length=255, blank=True)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inward {self.customer_name} - {self.email}"


class OutwardForm(models.Model):
    sent_by = models.CharField(max_length=255)
    approved_by = models.CharField(max_length=255)
    company_abbrev = models.CharField(max_length=255)

    # Destination details
    sent_to_company = models.CharField(max_length=255)
    sent_to_address = models.TextField()
    sent_to_district = models.CharField(max_length=255)
    sent_to_state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)

    # Inverter details
    inverter_id_outward = models.CharField(max_length=255)
    inverter_spec = models.CharField(max_length=255)
    inverter_rating = models.CharField(max_length=255, blank=True)
    battery = models.CharField(max_length=255, blank=True)

    # Replacement status
    inverter_replaced = models.CharField(max_length=10)
    replacement_type = models.CharField(max_length=255, blank=True)
    inverter_id_inward = models.CharField(max_length=255, blank=True)

    # Delivery
    delivered_through = models.CharField(max_length=255)
    awb_number = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Outward {self.inverter_id_outward} - {self.sent_to_company}"


class ServiceReportForm(models.Model):
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

# Employee Hierarchy Model
class Employee(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')

    def __str__(self):
        return self.name

class StockItem(models.Model):
    """Stock inventory for components and parts"""
    pcba_sn_old = models.CharField(max_length=100, blank=True, null=True, verbose_name="PCBA SN (old)")
    pcba_sn_new = models.CharField(max_length=100, db_index=True, verbose_name="PCBA SN (new)")
    component_type = models.CharField(max_length=255, blank=True, null=True)
    specification = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remark = models.TextField(blank=True, null=True)
    year = models.IntegerField(default=2025, db_index=True, help_text="Year of stock entry")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_items'
        verbose_name = 'Stock Item'
        verbose_name_plural = 'Stock Items'
        ordering = ['-year', 'component_type', 'pcba_sn_new']
        indexes = [
            models.Index(fields=['year', 'component_type']),
            models.Index(fields=['pcba_sn_new']),
        ]
    
    def __str__(self):
        return f"{self.pcba_sn_new} - {self.component_type or 'N/A'} ({self.year})"


class StockRequisition(models.Model):
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
