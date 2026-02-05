from django.contrib.admin import AdminSite

from .models import LeaveRequest
from .admin import LeaveRequestAdmin, LeaveReport, LeaveReportAdmin


class LeaveAdminSite(AdminSite):
    site_header = "Leave Administration"
    site_title = "Leave Admin"
    index_title = "Leave Management"

    def has_permission(self, request):
        """Allow only MuktaParanjape or superusers to access leave admin."""
        return request.user.is_active and (
            request.user.is_superuser or request.user.username == "MuktaParanjape"
        )

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["reports_url"] = "/leave-admin/forms/leavereport/"
        return super().index(request, extra_context)


leave_admin_site = LeaveAdminSite(name="leave_admin")
leave_admin_site.register(LeaveRequest, LeaveRequestAdmin)
leave_admin_site.register(LeaveReport, LeaveReportAdmin)