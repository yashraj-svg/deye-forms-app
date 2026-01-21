from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    # Namespace the app to support `{% url 'forms:...' %}` consistently
    path('', include(('forms.urls', 'forms'), namespace='forms')),
]
