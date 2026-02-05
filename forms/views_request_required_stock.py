

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from forms.models import StockRequisition, DispatchedStock
from django.db.models import Sum, Q
from django.http import HttpResponse, HttpResponseForbidden
from functools import wraps
import csv


def stock_manager_required(view_func):
    """Allow only superusers, SnehalShinde, or NileshBagad"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        allowed_users = {"SnehalShinde", "NileshBagad"}
        if not (request.user.is_superuser or request.user.username in allowed_users):
            return HttpResponseForbidden("⛔ Access Denied: Only stock managers (Snehal/Nilesh) or superusers can access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@stock_manager_required
def request_required_stock(request):
    # Filters
    serial_filter = request.GET.get('serial', '').strip()
    component_filter = request.GET.get('component', '').strip()
    min_qty = request.GET.get('min_qty', '').strip()
    max_qty = request.GET.get('max_qty', '').strip()
    export = request.GET.get('export', '')

    reqs = StockRequisition.objects.all()
    req_map = {}
    for req in reqs:
        key = (req.serial_number, req.component_type)
        if key not in req_map:
            req_map[key] = {'required': 0, 'approved': 0, 'dispatched': 0, 'description': req.description}
        req_map[key]['required'] += req.quantity_required
        req_map[key]['approved'] += req.approved_quantity or 0
    for disp in DispatchedStock.objects.all():
        key = (disp.serial_number, disp.component_type)
        if key in req_map:
            req_map[key]['dispatched'] += disp.quantity_dispatched
    required_stock = []
    for (serial, component), vals in req_map.items():
        already_sent = max(vals['approved'], vals['dispatched'])
        still_needed = vals['required'] - already_sent
        if still_needed > 0:
            required_stock.append({
                'serial_number': serial,
                'component_type': component,
                'description': vals['description'],
                'quantity_needed': still_needed
            })
    # Apply filters
    if serial_filter:
        required_stock = [row for row in required_stock if serial_filter.lower() in row['serial_number'].lower()]
    if component_filter:
        required_stock = [row for row in required_stock if component_filter.lower() in row['component_type'].lower()]
    if min_qty:
        try:
            min_qty_val = int(min_qty)
            required_stock = [row for row in required_stock if row['quantity_needed'] >= min_qty_val]
        except ValueError:
            pass
    if max_qty:
        try:
            max_qty_val = int(max_qty)
            required_stock = [row for row in required_stock if row['quantity_needed'] <= max_qty_val]
        except ValueError:
            pass

    # Export CSV
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="required_stock.csv"'
        writer = csv.writer(response)
        writer.writerow(['Serial Number', 'Component Type', 'Description', 'Quantity Needed'])
        for row in required_stock:
            writer.writerow([row['serial_number'], row['component_type'], row['description'], row['quantity_needed']])
        return response

    total_qty = sum(row['quantity_needed'] for row in required_stock)
    total_components = len(required_stock)
    return render(request, 'forms/request_required_stock.html', {
        'required_stock': required_stock,
        'serial_filter': serial_filter,
        'component_filter': component_filter,
        'min_qty': min_qty,
        'max_qty': max_qty,
        'total_qty': total_qty,
        'total_components': total_components,
    })
