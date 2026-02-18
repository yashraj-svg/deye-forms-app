from django.urls import path
from . import views
from .views_request_required_stock import request_required_stock
from .views import available_inverter_serials, available_battery_serials
from .views_fix_database import fix_railway_database

app_name = 'forms'

urlpatterns = [
    path('hierarchy/', views.hierarchy_static_view, name='hierarchy'),
    path('', views.simple_home, name='simple_home'),
    path('password-change/', views.change_password, name='change_password'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/id-card/', views.user_id_card, name='user_id_card'),
    path('profile/id-card/download/', views.download_id_card, name='download_id_card'),
    path('calculator/', views.freight_calculator, name='calculator'),
    path('calculator/diagnose/', views.bigship_diagnostic, name='bigship_diagnostic'),
    path('stock/', views.stock_home, name='stock'),
    path('stock/received/', views.received_stock, name='received_stock'),
    path('stock/fix-database/', fix_railway_database, name='fix_database'),
    path('stock/remaining/', views.remaining_stock, name='remaining_stock'),
    path('stock/send/', views.send_stock, name='send_stock'),
    path('stock/dispatched/', views.dispatched_stock, name='dispatched_stock'),
    path('stock/request-required/', request_required_stock, name='request_required_stock'),
    path('stock/update-new-shipments/', views.update_new_shipments, name='update_new_shipments'),
    path('api/pincode/', views.pincode_lookup_api, name='pincode_lookup'),
    path('api/awb-lookup/', views.awb_lookup_api, name='awb_lookup'),
    # Stock APIs
    path('api/stock/serial-search/', views.stock_serial_search, name='stock_serial_search'),
    path('api/stock/serial-details/', views.stock_serial_details, name='stock_serial_details'),
    path('api/stock-info/', views.stock_info_api, name='stock_info_api'),
    
    # User Registration
    path('register/', views.register, name='register'),
    
    # Birthday Greeting
    path('birthday/<int:user_id>/', views.birthday_greeting, name='birthday_greeting'),

    path('forms/', views.select_form_page, name='select_form'),

    path('forms/repairing/', views.repairing_form_page, name='repairing_form'),
    path('forms/inward/', views.inward_form_page, name='inward_form'),
    path('forms/outward/', views.outward_form_page, name='outward_form'),
    path('forms/service/', views.service_form_page, name='service_form'),
    path('forms/logistic/', views.logistic_booking_create, name='logistic_form'),
    path('forms/logistic/list/', views.logistic_booking_list, name='logistic_list'),
    path('forms/logistic/<int:booking_id>/edit/', views.logistic_booking_edit, name='logistic_edit'),
    path('forms/service-report/<int:report_id>/pdf/', views.service_report_pdf, name='service_report_pdf'),
    path('forms/data/', views.forms_data_overview, name='forms_data_overview'),
        path('forms/repairing/<int:form_id>/pdf/', views.repairing_form_pdf, name='repairing_form_pdf'),
        path('forms/inward/<int:form_id>/pdf/', views.inward_form_pdf, name='inward_form_pdf'),
        path('forms/outward/<int:form_id>/pdf/', views.outward_form_pdf, name='outward_form_pdf'),
    
    # Employee Data Dashboard
    path('my-data/', views.employee_data_view, name='my_data'),
    path('my-data/edit/<str:form_type>/<int:form_id>/', views.edit_employee_form, name='edit_employee_form'),
    path('my-data/export/<str:form_type>/<str:format>/', views.export_employee_data, name='export_employee_data'),
    path('team-data/', views.team_data_view, name='team_data'),
    path('team-data/export/<str:form_type>/<str:format>/', views.export_team_data, name='export_team_data'),
    path('team-data/stock-inverters/', views.stock_inverters_view, name='stock_inverters'),

    path('leave/', views.leave_home, name='leave_home'),
    path('leave/apply/', views.apply_leave, name='apply_leave'),
    path('leave/status/', views.leave_status, name='leave_status'),
    path('leave/history/', views.leave_history, name='leave_history'),
    path('leave/team-attendance/', views.team_attendance, name='team_attendance'),

    # Admin leave management
    path('leave/admin/', views.leave_admin, name='leave_admin'),
    path('leave/admin/export/', views.leave_export_csv, name='leave_export_csv'),
    path('leave/admin/report/', views.leave_admin_report, name='leave_admin_report'),
    path('leave/admin/<int:leave_id>/update/', views.update_leave_status, name='update_leave_status'),
    
    # Email approve/reject actions
    path('leave/email/approve/<int:leave_id>/', views.approve_leave_email, name='approve_leave_email'),
    path('leave/email/reject/<int:leave_id>/', views.reject_leave_email, name='reject_leave_email'),

    # Check-In / Check-Out
    path('checkin/', views.checkin_page, name='checkin_page'),
    path('api/checkin/submit/', views.checkin_submit, name='checkin_submit'),
    path('api/checkin/checkout/', views.checkout_submit, name='checkout_submit'),
    path('api/checkin/status/', views.get_checkin_status, name='get_checkin_status'),
    path('attendance/history/', views.attendance_history, name='attendance_history'),
    path('attendance/team/', views.manager_attendance_view, name='manager_attendance'),
    
    # Location Tracking (Hourly Pings & Travel History)
    path('api/location/ping/', views.save_location_ping, name='save_location_ping'),
    path('travel/history/', views.travel_history_view, name='travel_history'),
    path('travel/history/<str:username>/', views.travel_history_view, name='travel_history'),
    
    # Daily Travel Summary (Day-wise with total distance)
    path('travel/daily-summary/', views.daily_travel_summary_view, name='daily_travel_summary'),
    path('travel/daily-summary/<str:username>/', views.daily_travel_summary_view, name='daily_travel_summary'),
    path('travel/map/<str:username>/<str:date_str>/', views.day_route_map_view, name='day_route_map'),

    path('api/available-inverter-serials/', available_inverter_serials, name='available_inverter_serials'),
    path('api/available-battery-serials/', available_battery_serials, name='available_battery_serials'),
]
