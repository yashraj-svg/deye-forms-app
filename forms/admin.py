
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import LeaveRequest, UpcomingEvent, UserProfile, RepairingForm, InwardForm, OutwardForm, ServiceReportForm, StockItem, StockRequisition, DispatchedStock


# Inline for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'  # Specify which ForeignKey to use
    fields = ('date_of_birth', 'phone', 'department', 'manager', 'location', 'designation')


# Custom User Admin to show first name, last name, email on creation
# Unregister default UserAdmin first, then register custom one
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_date_of_birth', 'get_phone', 'is_staff')
    
    def get_date_of_birth(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.date_of_birth or '-'
        return '-'
    get_date_of_birth.short_description = 'Date of Birth'
    
    def get_phone(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.phone or '-'
        return '-'
    get_phone.short_description = 'Phone'


@admin.register(UpcomingEvent)
class UpcomingEventAdmin(admin.ModelAdmin):
    change_list_template = 'admin/forms/change_list.html'
    list_display = ('title', 'event_date', 'location', 'is_active')
    list_filter = ('is_active', 'event_date')
    search_fields = ('title', 'location', 'description')
    ordering = ('event_date',)
    actions = ['delete_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions


@admin.register(RepairingForm)
class RepairingFormAdmin(admin.ModelAdmin):
    change_list_template = 'admin/forms/change_list.html'
    list_display = ('case_number', 'repairing_object', 'inverter_id', 'inverter_spec', 'fault_preview', 'repaired_by', 'tested_by', 'repaired_on_date', 'image_preview_before', 'image_preview_after', 'created_at')
    search_fields = ('customer_abbrev', 'case_number', 'inverter_id', 'pcba_serial', 'repaired_by', 'tested_by')
    list_filter = ()  # Using header filters instead of sidebar filters
    readonly_fields = ('created_at', 'updated_at', 'image_preview_before_large', 'image_preview_after_large')
    actions = ['delete_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer_abbrev', 'case_number', 'repairing_object', 'created_at', 'updated_at')
        }),
        ('Inverter Details', {
            'fields': ('inverter_id', 'inverter_spec', 'inverter_rating', 'battery')
        }),
        ('Fault Details', {
            'fields': ('fault_problems', 'fault_description', 'fault_location', 'pcba_serial')
        }),
        ('Repair Information', {
            'fields': ('repair_content', 'repaired_by', 'tested_by', 'repaired_on_date', 'repaired_location', 'remark', 'pending_component')
        }),
        ('Images', {
            'fields': ('image_preview_before_large', 'image_preview_after_large'),
            'classes': ('wide',),
            'description': 'Click images to view full size'
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    def fault_preview(self, obj):
        if obj.fault_description:
            preview = obj.fault_description[:30] + '...' if len(obj.fault_description) > 30 else obj.fault_description
            return format_html('<span title="{}">{}</span>', obj.fault_description, preview)
        return '-'
    fault_preview.short_description = 'Fault'
    
    def image_preview_before(self, obj):
        if obj.image_before:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px; cursor: pointer;" '
                'onclick="window.open(\'{}\', \'_blank\')" alt="Before">',
                obj.image_before, obj.image_before
            )
        return '-'
    image_preview_before.short_description = 'Before 🔍'
    
    def image_preview_after(self, obj):
        if obj.image_after:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px; cursor: pointer;" '
                'onclick="window.open(\'{}\', \'_blank\')" alt="After">',
                obj.image_after, obj.image_after
            )
        return '-'
    image_preview_after.short_description = 'After 🔍'
    
    def image_preview_before_large(self, obj):
        if obj.image_before:
            return format_html(
                '<img src="{}" style="max-width: 100%; max-height: 400px; border-radius: 8px; border: 2px solid #e3e6e9;">',
                obj.image_before
            )
        return format_html('<span style="color: #999;">No image uploaded</span>')
    image_preview_before_large.short_description = 'Before Image (Full Size)'
    
    def image_preview_after_large(self, obj):
        if obj.image_after:
            return format_html(
                '<img src="{}" style="max-width: 100%; max-height: 400px; border-radius: 8px; border: 2px solid #e3e6e9;">',
                obj.image_after
            )
        return format_html('<span style="color: #999;">No image uploaded</span>')
    image_preview_after_large.short_description = 'After Image (Full Size)'


@admin.register(InwardForm)
class InwardFormAdmin(admin.ModelAdmin):
    change_list_template = 'admin/forms/change_list.html'
    list_display = ('email', 'received_by', 'customer_abbrev', 'customer_name', 'received_from_location', 'received_from_district', 'received_from_state', 'pincode', 'inverter_id', 'inverter_specs', 'inverter_ratings', 'battery', 'reason', 'transportation_mode', 'awb_lr_number', 'remarks', 'created_at')
    search_fields = ('email', 'customer_name', 'inverter_id', 'awb_lr_number', 'customer_abbrev', 'reason')
    list_filter = ()  # Using header filters instead of sidebar filters
    readonly_fields = ('created_at', 'updated_at')
    actions = ['delete_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }


@admin.register(OutwardForm)
class OutwardFormAdmin(admin.ModelAdmin):
    change_list_template = 'admin/forms/change_list.html'
    list_display = ('sent_by', 'approved_by', 'company_abbrev', 'sent_to_company', 'sent_to_address', 'sent_to_district', 'sent_to_state', 'pincode', 'inverter_id_outward', 'inverter_spec', 'inverter_rating', 'battery', 'inverter_replaced', 'replacement_type', 'inverter_id_inward', 'delivered_through', 'awb_number', 'created_at')
    search_fields = ('sent_to_company', 'inverter_id_outward', 'awb_number', 'company_abbrev', 'sent_by', 'approved_by')
    list_filter = ()  # Using header filters instead of sidebar filters
    readonly_fields = ('created_at', 'updated_at')
    actions = ['delete_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }


@admin.register(ServiceReportForm)
class ServiceReportFormAdmin(admin.ModelAdmin):
    change_list_template = 'admin/forms/change_list.html'
    # Comprehensive list_display showing ALL key fields like Excel
    list_display = (
        'engineer_display', 'customer_display', 'date_of_service', 'phone_number',
        'product_type', 'serial_number', 'inverter_capacity', 'pv_capacity_kw', 'no_of_mppt',
        'dc_checks_display', 'ac_checks_display', 'earthing_checks_display',
        'physical_obs_preview', 'battery_type', 'battery_make', 'battery_voltage',
        'work_done_preview', 'cause_preview', 'protocol_preview', 'conclusion_preview',
        'created_at'
    )
    
    # Enhanced search across all important fields
    search_fields = (
        'email', 'phone_number', 'engineer_first_name', 'engineer_last_name',
        'customer_first_name', 'customer_last_name', 'serial_number', 'product_type',
        'address_city', 'address_state', 'battery_make', 'protocol'
    )
    
    # No sidebar filters - column filtering will be handled via JavaScript
    list_filter = ()
    
    readonly_fields = ('created_at', 'updated_at', 'engineer_sig_large', 'customer_sig_large')
    actions = ['delete_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
    
    fieldsets = (
        ('Date & Contact', {
            'fields': ('date_of_service', 'phone_number', 'email', 'created_at', 'updated_at')
        }),
        ('Engineer Information', {
            'fields': ('engineer_first_name', 'engineer_last_name')
        }),
        ('Customer Information', {
            'fields': ('customer_first_name', 'customer_last_name', 'address_street', 'address_city', 'address_state', 'address_zip')
        }),
        ('Product Information', {
            'fields': ('product_type', 'serial_number', 'inverter_capacity', 'pv_capacity_kw', 'no_of_mppt', 'lcd_version', 'mcu_version')
        }),
        ('Component Checks', {
            'fields': ('dc_spd', 'dc_switch', 'dc_fuse', 'ac_spd', 'ac_switch', 'ac_fuse', 'earthing_panel', 'earthing_inverter', 'earthing_ac_neutral', 'ac_neutral_earth_voltage', 'ac_cable_size'),
            'classes': ('collapse',)
        }),
        ('Physical & Work Details', {
            'fields': ('physical_observation', 'actual_work_done', 'cause_of_failure')
        }),
        ('Repair Work', {
            'fields': ('repair_inverter', 'repair_dust', 'repair_cabling', 'repair_other'),
            'classes': ('collapse',)
        }),
        ('DC Side Measurements (PV Data)', {
            'fields': (),
            'classes': ('collapse',),
            'description': 'PV array measurements are displayed in a table below the form'
        }),
        ('AC Side Measurements (AC Data)', {
            'fields': (),
            'classes': ('collapse',),
            'description': 'AC phase measurements are displayed in a table below the form'
        }),
        ('Battery Information', {
            'fields': ('battery_type', 'battery_make', 'battery_voltage', 'no_of_battery', 'battery_protection', 'battery_bms_make', 'battery_bms_model', 'battery_bms_ratings'),
            'classes': ('collapse',)
        }),
        ('Assessment & Protocol', {
            'fields': ('protocol', 'conclusion', 'customer_ratings', 'suggestions')
        }),
        ('Signatures (Click to view full size)', {
            'fields': ('engineer_sig_large', 'customer_sig_large'),
            'classes': ('wide',)
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    def engineer_display(self, obj):
        return format_html('{} {}', obj.engineer_first_name, obj.engineer_last_name)
    engineer_display.short_description = 'Engineer'
    
    def customer_display(self, obj):
        return format_html('{} {}', obj.customer_first_name, obj.customer_last_name)
    customer_display.short_description = 'Customer'
    
    def dc_checks_display(self, obj):
        checks = []
        if obj.dc_spd: checks.append('SPD')
        if obj.dc_switch: checks.append('SW')
        if obj.dc_fuse: checks.append('FU')
        return format_html('<span style="color: #27ae60; font-weight: bold;">{}</span>', ', '.join(checks) if checks else '—')
    dc_checks_display.short_description = 'DC ✓'
    
    def ac_checks_display(self, obj):
        checks = []
        if obj.ac_spd: checks.append('SPD')
        if obj.ac_switch: checks.append('SW')
        if obj.ac_fuse: checks.append('FU')
        return format_html('<span style="color: #27ae60; font-weight: bold;">{}</span>', ', '.join(checks) if checks else '—')
    ac_checks_display.short_description = 'AC ✓'
    
    def earthing_checks_display(self, obj):
        checks = []
        if obj.earthing_panel: checks.append('Pan')
        if obj.earthing_inverter: checks.append('Inv')
        if obj.earthing_ac_neutral: checks.append('Neu')
        return format_html('<span style="color: #27ae60; font-weight: bold;">{}</span>', ', '.join(checks) if checks else '—')
    earthing_checks_display.short_description = 'Earth ✓'
    
    def physical_obs_preview(self, obj):
        if obj.physical_observation:
            preview = obj.physical_observation[:15] + '...' if len(obj.physical_observation) > 15 else obj.physical_observation
            return format_html('<span title="{}">{}</span>', obj.physical_observation, preview)
        return '—'
    physical_obs_preview.short_description = 'Observation'
    
    def battery_display(self, obj):
        if obj.battery_make:
            return format_html('{} {}', obj.battery_make, obj.battery_voltage or '')
        return '—'
    battery_display.short_description = 'Battery Info'
    
    def work_done_preview(self, obj):
        if obj.actual_work_done:
            preview = obj.actual_work_done[:15] + '...' if len(obj.actual_work_done) > 15 else obj.actual_work_done
            return format_html('<span title="{}">{}</span>', obj.actual_work_done, preview)
        return '—'
    work_done_preview.short_description = 'Work Done'
    
    def cause_preview(self, obj):
        if obj.cause_of_failure:
            preview = obj.cause_of_failure[:15] + '...' if len(obj.cause_of_failure) > 15 else obj.cause_of_failure
            return format_html('<span title="{}">{}</span>', obj.cause_of_failure, preview)
        return '—'
    cause_preview.short_description = 'Cause'
    
    def protocol_preview(self, obj):
        if obj.protocol:
            preview = obj.protocol[:12] + '...' if len(obj.protocol) > 12 else obj.protocol
            return format_html('<span title="{}">{}</span>', obj.protocol, preview)
        return '—'
    protocol_preview.short_description = 'Protocol'
    
    def conclusion_preview(self, obj):
        if obj.conclusion:
            preview = obj.conclusion[:12] + '...' if len(obj.conclusion) > 12 else obj.conclusion
            return format_html('<span title="{}">{}</span>', obj.conclusion, preview)
        return '—'
    conclusion_preview.short_description = 'Conclusion'
    
    def engineer_sig_preview(self, obj):
        if obj.engineer_signature_data:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px; cursor: pointer; border: 1px solid #ddd;" '
                'onclick="window.open(\'{}\', \'_blank\')" alt="Engineer Signature" title="Click to view full size">',
                obj.engineer_signature_data, obj.engineer_signature_data
            )
        return '—'
    engineer_sig_preview.short_description = 'Eng Sig'
    
    def customer_sig_preview(self, obj):
        if obj.customer_signature_data:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px; cursor: pointer; border: 1px solid #ddd;" '
                'onclick="window.open(\'{}\', \'_blank\')" alt="Customer Signature" title="Click to view full size">',
                obj.customer_signature_data, obj.customer_signature_data
            )
        return '—'
    customer_sig_preview.short_description = 'Cust Sig'
    
    def pv_data_table(self, obj):
        if not obj.pv_data:
            return format_html('<span style="color: #999;">No PV data recorded</span>')
        
        html = '<table style="border-collapse: collapse; width: 100%; margin: 10px 0;">'
        html += '<thead style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"><tr style="color: white;">'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">PV</th>'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">Voltage (V)</th>'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">Current (A)</th>'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">Earthing</th>'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">PV Panel</th>'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">Observation</th>'
        html += '</tr></thead><tbody>'
        
        for idx, row in enumerate(obj.pv_data):
            bg_color = '#fafbfc' if idx % 2 == 0 else '#ffffff'
            html += f'<tr style="background-color: {bg_color};">'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;"><strong>{row.get("pv", "—")}</strong></td>'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row.get("voltage", "—")}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row.get("current", "—")}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row.get("earthing", "—")}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row.get("panel", "—")}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row.get("observation", "—")}</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return format_html(html)
    pv_data_table.short_description = 'PV Measurements'
    
    def ac_data_table(self, obj):
        if not obj.ac_data:
            return format_html('<span style="color: #999;">No AC data recorded</span>')
        
        html = '<table style="border-collapse: collapse; width: 100%; margin: 10px 0;">'
        html += '<thead style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"><tr style="color: white;">'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">Phase</th>'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">Voltage (V)</th>'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">Current (A)</th>'
        html += '<th style="border: 1px solid #ddd; padding: 10px; font-weight: 600;">Earthing</th>'
        html += '</tr></thead><tbody>'
        
        # Define phase mapping for better display
        phase_labels = {
            'R_TO_N': 'R TO N',
            'Y_TO_N': 'Y TO N',
            'B_TO_N': 'B TO N',
            'R_TO_Y': 'R TO Y',
            'Y_TO_B': 'Y TO B',
            'B_TO_R': 'B TO R',
            'N_TO_PE': 'N TO PE'
        }
        
        for idx, (phase_key, phase_data) in enumerate(obj.ac_data.items()):
            phase_label = phase_labels.get(phase_key, phase_key)
            bg_color = '#fafbfc' if idx % 2 == 0 else '#ffffff'
            html += f'<tr style="background-color: {bg_color};">'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;"><strong>{phase_label}</strong></td>'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;">{phase_data.get("voltage", "—")}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;">{phase_data.get("current", "—")}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 10px;">{phase_data.get("earthing", "—")}</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return format_html(html)
    ac_data_table.short_description = 'AC Measurements'
    
    def engineer_sig_large(self, obj):
        if obj.engineer_signature_data:
            return format_html(
                '<div style="border: 2px solid #e3e6e9; border-radius: 8px; padding: 10px; background: #f9fafb;">'
                '<img src="{}" style="max-width: 100%; max-height: 300px; border-radius: 4px;" alt="Engineer Signature">'
                '</div>',
                obj.engineer_signature_data
            )
        return format_html('<span style="color: #999;">No signature uploaded</span>')
    engineer_sig_large.short_description = 'Engineer Signature (Full Size)'
    
    def customer_sig_large(self, obj):
        if obj.customer_signature_data:
            return format_html(
                '<div style="border: 2px solid #e3e6e9; border-radius: 8px; padding: 10px; background: #f9fafb;">'
                '<img src="{}" style="max-width: 100%; max-height: 300px; border-radius: 4px;" alt="Customer Signature">'
                '</div>',
                obj.customer_signature_data
            )
        return format_html('<span style="color: #999;">No signature uploaded</span>')
    customer_sig_large.short_description = 'Customer Signature (Full Size)'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    change_list_template = 'admin/forms/change_list.html'
    list_display = (
        'employee_name',
        'leave_type_display',
        'date_range',
        'total_days_display',
        'status_badge',
        'applied_at_display',
        'status_changed_display',
        'changed_by_display'
    )
    list_filter = ()  # Header filters will handle filtering
    search_fields = ('user__username', 'user__email', 'reason')
    readonly_fields = ('applied_at', 'status_changed_at', 'status_changed_by', 'total_days', 'computed_days')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('user',)
        }),
        ('Leave Details', {
            'fields': ('leave_type', 'start_date', 'end_date', 'start_breakdown', 'end_breakdown', 'computed_days', 'total_days', 'reason')
        }),
        ('Status & Approval', {
            'fields': ('status', 'applied_at', 'status_changed_at', 'status_changed_by')
        }),
    )
    
    actions = ['approve_leave', 'reject_leave', 'delete_selected', 'export_as_csv']

    def get_actions(self, request):
        """Get available actions based on user permissions"""
        actions = super().get_actions(request)
        
        # Only superusers can delete
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        
        return actions

    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    def has_module_permission(self, request):
        """Only MuktaParanjape or superusers can access Leave admin"""
        if request.user.is_superuser or request.user.username == 'MuktaParanjape':
            return True
        return False
    
    def has_view_permission(self, request, obj=None):
        """Only MuktaParanjape or superusers can view leaves"""
        if request.user.is_superuser or request.user.username == 'MuktaParanjape':
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """Only MuktaParanjape or superusers can change leaves"""
        if request.user.is_superuser or request.user.username == 'MuktaParanjape':
            return True
        return False
    
    def has_add_permission(self, request):
        """Only MuktaParanjape or superusers can add leaves"""
        if request.user.is_superuser or request.user.username == 'MuktaParanjape':
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete leaves"""
        return request.user.is_superuser
    
    def employee_name(self, obj):
        return format_html(
            '<strong>{}</strong>',
            obj.user.get_username()
        )
    employee_name.short_description = 'Employee'
    
    def leave_type_display(self, obj):
        return obj.get_leave_type_display()
    leave_type_display.short_description = 'Type'
    
    def date_range(self, obj):
        return format_html(
            '{} ({}) → {} ({})',
            obj.start_date,
            obj.start_breakdown,
            obj.end_date,
            obj.end_breakdown
        )
    date_range.short_description = 'Date Range'
    
    def total_days_display(self, obj):
        return f'{obj.total_days:.1f}'
    total_days_display.short_description = 'Days'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#fff3cd',
            'approved': '#d4edda',
            'rejected': '#f8d7da',
        }
        text_colors = {
            'pending': '#856404',
            'approved': '#155724',
            'rejected': '#721c24',
        }
        color = colors.get(obj.status, '#e2e3e5')
        text_color = text_colors.get(obj.status, '#383d41')
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; display: inline-block;">{}</span>',
            color,
            text_color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def applied_at_display(self, obj):
        if obj.applied_at:
            return obj.applied_at.strftime('%Y-%m-%d %H:%M')
        return '—'
    applied_at_display.short_description = 'Applied At'
    
    def status_changed_display(self, obj):
        if obj.status_changed_at:
            return obj.status_changed_at.strftime('%Y-%m-%d %H:%M')
        return '—'
    status_changed_display.short_description = 'Last Updated'
    
    def changed_by_display(self, obj):
        if obj.status_changed_by:
            return obj.status_changed_by.get_username()
        return '—'
    changed_by_display.short_description = 'Updated By'
    
    def computed_days(self, obj):
        days = f'{obj.compute_total_days():.1f}'
        return days
    computed_days.short_description = 'Computed Days (Excluding Sundays)'
    
    def save_model(self, request, obj, form, change):
        """Override save to track status changes"""
        if change and 'status' in form.changed_data:
            obj.status_changed_at = timezone.now()
            obj.status_changed_by = request.user
            
            # Notify user of status change via SendGrid Web API
            if obj.user.email:
                from forms.emails import send_sendgrid_email
                import threading
                
                def _send_status_email():
                    message = (
                        f"Hello {obj.user.get_username()},\n\n"
                        f"Your leave request from {obj.start_date} to {obj.end_date} is now {obj.status.title()}.\n"
                        f"Total days: {obj.total_days}."
                    )
                    send_sendgrid_email(
                        [obj.user.email],
                        'Leave status updated',
                        f"<p>{message.replace(chr(10), '<br>')}</p>",
                        message
                    )
                
                email_thread = threading.Thread(target=_send_status_email, daemon=False)
                email_thread.start()
        
        super().save_model(request, obj, form, change)
    
    def approve_leave(self, request, queryset):
        """Bulk action to approve leave requests"""
        count = 0
        for leave in queryset.filter(status='pending'):
            leave.status = 'approved'
            leave.status_changed_at = timezone.now()
            leave.status_changed_by = request.user
            leave.save()
            
            # Notify employee via SendGrid Web API
            if leave.user.email:
                from forms.emails import send_sendgrid_email
                import threading
                
                def _send_approval_email():
                    message = (
                        f"Hello {leave.user.get_username()},\n\n"
                        f"Your leave request from {leave.start_date} to {leave.end_date} has been approved.\n"
                        f"Total days: {leave.total_days}."
                    )
                    send_sendgrid_email(
                        [leave.user.email],
                        'Leave Approved',
                        f"<p>{message.replace(chr(10), '<br>')}</p>",
                        message
                    )
                
                email_thread = threading.Thread(target=_send_approval_email, daemon=False)
                email_thread.start()
            count += 1
        
        self.message_user(request, f'{count} leave request(s) approved.')
    approve_leave.short_description = 'Approve selected leave requests'
    
    def reject_leave(self, request, queryset):
        """Bulk action to reject leave requests"""
        count = 0
        for leave in queryset.filter(status='pending'):
            leave.status = 'rejected'
            leave.status_changed_at = timezone.now()
            leave.status_changed_by = request.user
            leave.save()
            
            # Notify employee via SendGrid Web API
            if leave.user.email:
                from forms.emails import send_sendgrid_email
                import threading
                
                def _send_rejection_email():
                    message = (
                        f"Hello {leave.user.get_username()},\n\n"
                        f"Your leave request from {leave.start_date} to {leave.end_date} has been rejected."
                    )
                    send_sendgrid_email(
                        [leave.user.email],
                        'Leave Rejected',
                        f"<p>{message.replace(chr(10), '<br>')}</p>",
                        message
                    )
                
                email_thread = threading.Thread(target=_send_rejection_email, daemon=False)
                email_thread.start()
            count += 1
        
        self.message_user(request, f'{count} leave request(s) rejected.')
    reject_leave.short_description = 'Reject selected leave requests'
    
    def export_as_csv(self, request, queryset):
        """Export selected leave requests as CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leave_requests.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Employee', 'Type', 'Start', 'End', 'Start Portion', 'End Portion',
            'Total Days', 'Status', 'Applied At', 'Status Changed At', 'Changed By', 'Reason'
        ])
        for leave in queryset:
            writer.writerow([
                leave.user.get_username(),
                leave.get_leave_type_display(),
                leave.start_date,
                leave.end_date,
                leave.start_breakdown,
                leave.end_breakdown,
                leave.total_days,
                leave.status,
                leave.applied_at,
                leave.status_changed_at,
                leave.status_changed_by.get_username() if leave.status_changed_by else '',
                leave.reason,
            ])
        return response
    export_as_csv.short_description = 'Export selected leave requests to CSV'
    
    class Media:
        css = {
            'all': ('admin/css/leave_admin.css',)
        }


# Custom admin site to add Reports
class DeyeAdminSite(admin.AdminSite):
    site_header = "Deye Web App Administration"
    site_title = "Deye Admin"
    index_title = "Welcome to Deye Administration"
    
    def index(self, request, extra_context=None):
        """Add Reports link to admin index"""
        extra_context = extra_context or {}
        extra_context['reports_url'] = '/admin/forms/leavereport/'
        return super().index(request, extra_context)


# Create a model to display reports (read-only)
from django.db import models

class LeaveReport(models.Model):
    """Virtual model for displaying leave reports - not stored in database"""
    class Meta:
        app_label = 'forms'
        verbose_name = 'Leave Report'
        verbose_name_plural = 'Leave Reports'
        managed = False


@admin.register(LeaveReport)
class LeaveReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/leave_report_changelist.html'

    def has_module_permission(self, request):
        """Only MuktaParanjape or superusers can access Leave Reports."""
        return request.user.is_superuser or request.user.username == 'MuktaParanjape'

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.username == 'MuktaParanjape'

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.username == 'MuktaParanjape'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        """Return empty queryset since this is a virtual model"""
        return LeaveReport.objects.none()
    
    def changelist_view(self, request, extra_context=None):
        """Custom view to display employee-wise leave statistics"""
        from datetime import date
        from django.db.models import Sum
        
        today = date.today()
        current_year = today.year
        
        # Get all users with at least one leave request
        employees = User.objects.filter(
            leaverequest__isnull=False
        ).distinct().order_by('username')
        
        report_data = []
        for employee in employees:
            # Total requests
            total_requests = LeaveRequest.objects.filter(
                user=employee,
                leave_type='leave'
            ).count()
            
            # Total approved (paid leave only)
            total_approved = LeaveRequest.objects.filter(
                user=employee,
                leave_type='leave',
                status='approved'
            ).aggregate(total=Sum('total_days'))['total'] or 0.0
            
            # Total rejected
            total_rejected = LeaveRequest.objects.filter(
                user=employee,
                leave_type='leave',
                status='rejected'
            ).count()
            
            # Total taken (approved leaves this year only)
            total_taken = LeaveRequest.objects.filter(
                user=employee,
                leave_type='leave',
                status='approved',
                start_date__year=current_year,
            ).aggregate(total=Sum('total_days'))['total'] or 0.0
            
            # Remaining leaves (for current year)
            remaining = max(21.0 - total_taken, 0.0)
            
            report_data.append({
                'employee': employee,
                'username': employee.get_username(),
                'total_requests': total_requests,
                'total_approved': f'{total_approved:.1f}',
                'total_rejected': total_rejected,
                'total_taken': f'{total_taken:.1f}',
                'remaining': f'{remaining:.1f}',
            })
        
        extra_context = extra_context or {}
        extra_context['report_data'] = report_data
        extra_context['current_year'] = current_year
        extra_context['title'] = 'Employee Leave Statistics Report'
        
        # Temporarily override the queryset to prevent database query
        self.queryset = lambda r: LeaveReport.objects.none()
        
        return super().changelist_view(request, extra_context)


# ─────────────────────────────
# Stock Inventory Admin
# ─────────────────────────────

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    # NO custom template - use default Django admin template
    # change_list_template = 'admin/forms/change_list.html'
    list_display = ('pcba_sn_new', 'component_type', 'specification', 'quantity', 'year', 'shipment_date', 'created_at')
    list_filter = ('year', 'component_type', 'shipment_date', 'created_at')
    search_fields = ('pcba_sn_new', 'pcba_sn_old', 'component_type', 'specification', 'remark')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    actions = ['delete_selected']
    
    # Make visible to all staff, not just superusers
    def has_module_permission(self, request):
        return request.user.is_staff or request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
    
    fieldsets = (
        ('Identification', {
            'fields': ('pcba_sn_new', 'pcba_sn_old', 'year', 'shipment_date')
        }),
        ('Component Details', {
            'fields': ('component_type', 'specification', 'quantity')
        }),
        ('Additional Information', {
            'fields': ('remark',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockRequisition)
class StockRequisitionAdmin(admin.ModelAdmin):
    change_list_template = 'admin/forms/change_list.html'
    list_display = ('serial_number', 'component_type', 'manager_name', 'quantity_required', 'approved_quantity', 'required_to', 'status', 'created_at')
    search_fields = ('serial_number', 'manager_name', 'description', 'required_to')
    list_filter = ('status', 'component_type', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'current_stock', 'remaining_after_requested', 'remaining_after_approved')

    class Media:
        js = ('admin/js/stock_requisition_admin.js',)
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
    
    fieldsets = (
        ('Requisition Details', {
            'fields': ('serial_number', 'component_type', 'description')
        }),
        ('Engineer & Location', {
            'fields': ('manager_name', 'required_to')
        }),
        ('Quantity & Approval', {
            'fields': ('quantity_required', 'approved_quantity', 'status'),
            'description': 'Set approved_quantity to the amount you want to send (if different from requested).'
        }),
        ('Stock Information', {
            'fields': ('current_stock', 'remaining_after_requested', 'remaining_after_approved'),
            'description': 'Stock information based on requested and approved quantities.'
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_stock(self, obj):
        """Display current stock for the requisitioned serial number."""
        from .models import StockItem
        stock_item = StockItem.objects.filter(pcba_sn_new=obj.serial_number).order_by('-year').first()
        return stock_item.quantity if stock_item else 0
    current_stock.short_description = 'Current Stock (PCS)'
    
    def remaining_after_requested(self, obj):
        """Display remaining stock if the requested quantity is approved."""
        from .models import StockItem
        stock_item = StockItem.objects.filter(pcba_sn_new=obj.serial_number).order_by('-year').first()
        current = stock_item.quantity if stock_item else 0
        remaining = current - obj.quantity_required
        color = 'green' if remaining >= 0 else 'red'
        return f'<span style="color: {color}; font-weight: bold;">{remaining} PCS</span>'
    remaining_after_requested.short_description = 'Remaining (If Requested Qty Approved)'
    remaining_after_requested.allow_tags = True
    
    def remaining_after_approved(self, obj):
        """Display remaining stock based on approved_quantity if set, else requested_quantity."""
        from .models import StockItem
        stock_item = StockItem.objects.filter(pcba_sn_new=obj.serial_number).order_by('-year').first()
        current = stock_item.quantity if stock_item else 0
        qty_to_send = obj.approved_quantity if obj.approved_quantity is not None else obj.quantity_required
        remaining = current - qty_to_send
        color = 'green' if remaining >= 0 else 'red'
        return f'<span style="color: {color}; font-weight: bold;">{remaining} PCS</span>'
    remaining_after_approved.short_description = 'Remaining (If Approved Qty Sent)'
    remaining_after_approved.allow_tags = True
    
    actions = ['approve_requisitions', 'reject_requisitions', 'delete_selected']
    
    def approve_requisitions(self, request, queryset):
        """Admin action to approve selected requisitions."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user.username,
            approval_date=timezone.now()
        )
        self.message_user(request, f'{updated} requisition(s) approved successfully.')
    approve_requisitions.short_description = 'Approve selected requisitions'
    
    def reject_requisitions(self, request, queryset):
        """Admin action to reject selected requisitions."""
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} requisition(s) rejected.')
    reject_requisitions.short_description = 'Reject selected requisitions'


@admin.register(DispatchedStock)
class DispatchedStockAdmin(admin.ModelAdmin):
    change_list_template = 'admin/forms/change_list.html'
    list_display = [
        'serial_number',
        'component_type',
        'quantity_dispatched',
        'engineer_name',
        'dispatch_location',
        'dispatch_date',
        'courier_name',
        'tracking_number',
        'dispatched_by',
        'created_at'
    ]
    list_filter = ['dispatch_date', 'courier_name', 'dispatched_by', 'created_at']
    search_fields = ['serial_number', 'component_type', 'engineer_name', 'tracking_number', 'dispatch_location']
    readonly_fields = ['dispatched_by', 'created_at', 'updated_at']
    date_hierarchy = 'dispatch_date'
    actions = ['delete_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
    
    fieldsets = (
        ('Requisition Details', {
            'fields': ('requisition', 'serial_number', 'component_type')
        }),
        ('Dispatch Information', {
            'fields': (
                'quantity_dispatched',
                'engineer_name',
                'dispatch_location',
                'dispatch_date',
                'courier_name',
                'tracking_number',
                'dispatch_remarks'
            )
        }),
        ('Metadata', {
            'fields': ('dispatched_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set dispatched_by on creation
            obj.dispatched_by = request.user
        super().save_model(request, obj, form, change)
