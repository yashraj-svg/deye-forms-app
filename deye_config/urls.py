from django.contrib import admin
from django.urls import path, include
from forms.leave_admin_site import leave_admin_site

# Override admin site permission to allow only superusers
class SuperuserAdminSite(admin.AdminSite):
    def has_permission(self, request):
        """Only superusers can access admin panel"""
        return request.user.is_active and request.user.is_superuser

# Use custom admin site
admin_site = SuperuserAdminSite(name='admin')
admin_site._registry = admin.site._registry  # Copy all registered models
admin.site = admin_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('leave-admin/', leave_admin_site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    # Namespace the app to support `{% url 'forms:...' %}` consistently
    path('', include(('forms.urls', 'forms'), namespace='forms')),
]
