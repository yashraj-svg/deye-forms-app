import os
from django.contrib.auth.decorators import login_required

# Update New Shipments view (same interface as send_stock)
from django.http import HttpResponseForbidden
@login_required
def update_new_shipments(request):
    # Restrict access to SnehalShine, Nilesh, or superusers only
    allowed_users = {"SnehalShine", "Nilesh"}
    if not (request.user.is_superuser or request.user.username in allowed_users):
        return HttpResponseForbidden("You do not have permission to access this page.")
    from django.forms import formset_factory
    from .forms import StockRequisitionItemForm
    ItemFormSet = formset_factory(StockRequisitionItemForm, extra=0, can_delete=True)

    if request.method == 'POST':
        # Step 1: Data entry POST, show confirmation page
        if 'confirm_update' not in request.POST:
            item_formset = ItemFormSet(request.POST, prefix='form')
            if item_formset.is_valid():
                # Prepare summary data for confirmation, but pass the formset to the template
                total_qty = 0
                for form in item_formset:
                    if form.cleaned_data.get('serial_number') and not form.cleaned_data.get('DELETE'):
                        qty = form.cleaned_data.get('quantity_received') or 0
                        total_qty += float(qty)
                return render(request, 'forms/update_new_shipments_confirm.html', {
                    'item_formset': item_formset,
                    'total_qty': total_qty,
                })
            else:
                return render(request, 'forms/update_new_shipments.html', {
                    'item_formset': item_formset,
                    'empty_form': item_formset.empty_form,
                })
        # Step 2: Confirm Update POST, save to DB and send email
        else:
            # Save to DB using the formset so all edits and unique items are saved
            from .models import StockItem
            from django.core.mail import EmailMultiAlternatives
            from django.utils.html import escape
            item_formset = ItemFormSet(request.POST, prefix='form')
            items = []
            total_qty = 0
            shipment_date = request.POST.get('shipment_date')
            if item_formset.is_valid():
                for form in item_formset:
                    if form.cleaned_data.get('DELETE'):
                        continue
                    sn = form.cleaned_data.get('serial_number')
                    ct = form.cleaned_data.get('component_type')
                    desc = form.cleaned_data.get('description')
                    qty = form.cleaned_data.get('quantity_received') or 0
                    total_qty += float(qty)
                    items.append({'serial_number': sn, 'component_type': ct, 'description': desc, 'quantity_received': qty})
                    StockItem.objects.create(
                        pcba_sn_new=sn,
                        component_type=ct,
                        specification=desc,
                        quantity=qty,
                        year=(int(shipment_date[:4]) if shipment_date else 2026),
                        shipment_date=shipment_date
                    )
                
                # Send email notification
                try:
                    # Build email content
                    items_html = ""
                    for item in items:
                        items_html += f"""
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; text-align: left;">{escape(item['serial_number'])}</td>
                            <td style="padding: 10px; text-align: left;">{escape(item['component_type'])}</td>
                            <td style="padding: 10px; text-align: left;">{escape(item['description'])}</td>
                            <td style="padding: 10px; text-align: right;">{item['quantity_received']}</td>
                        </tr>
                        """
                    
                    email_html = f"""
                    <html style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc;">
                    <body style="margin: 0; padding: 20px; background: #f8fafc;">
                        <div style="max-width: 700px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08); overflow: hidden;">
                            <!-- Header -->
                            <div style="background: linear-gradient(135deg, #059669, #10b981); padding: 30px 20px; text-align: center; color: white;">
                                <h1 style="margin: 0; font-size: 28px; font-weight: 700;">📦 New Shipment Received</h1>
                                <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">Stock Update Notification</p>
                            </div>
                            
                            <!-- Content -->
                            <div style="padding: 30px;">
                                <p style="margin: 0 0 20px 0; font-size: 15px; color: #475569;">
                                    Hello,<br><br>
                                    A new shipment has been successfully added to the inventory system. Details are provided below:
                                </p>
                                
                                <!-- Shipment Details -->
                                <div style="background: #f1f5f9; border-left: 4px solid #059669; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                                    <p style="margin: 0; font-size: 14px; font-weight: 600; color: #0f172a;">Shipment Date:</p>
                                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #475569;">{escape(shipment_date or 'Not specified')}</p>
                                </div>
                                
                                <!-- Items Table -->
                                <p style="margin: 0 0 12px 0; font-size: 13px; font-weight: 700; color: #475569; text-transform: uppercase;">📋 Items Added ({len(items)})</p>
                                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px;">
                                    <thead>
                                        <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                                            <th style="padding: 10px; text-align: left; font-weight: 600; color: #475569;">Serial Number</th>
                                            <th style="padding: 10px; text-align: left; font-weight: 600; color: #475569;">Component Type</th>
                                            <th style="padding: 10px; text-align: left; font-weight: 600; color: #475569;">Description</th>
                                            <th style="padding: 10px; text-align: right; font-weight: 600; color: #475569;">Quantity</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {items_html}
                                    </tbody>
                                </table>
                                
                                <!-- Total -->
                                <div style="background: #ecfdf5; border-left: 4px solid #16a34a; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                                    <p style="margin: 0; font-size: 14px; font-weight: 600; color: #15803d;">
                                        💰 Total Quantity Received: <span style="font-size: 20px;">{int(total_qty)}</span> units
                                    </p>
                                </div>
                                
                                <p style="margin: 20px 0 0 0; font-size: 13px; color: #64748b;">
                                    You can view and manage this shipment in the inventory management system.
                                </p>
                            </div>
                            
                            <!-- Footer -->
                            <div style="background: #f1f5f9; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0; font-size: 12px; color: #64748b;">
                                    This is an automated notification from Deye Forms App.<br>
                                    <a href="https://www.deyeindia.in" style="color: #059669; text-decoration: none;">www.deyeindia.in</a>
                                </p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Prepare email
                    subject = f"📦 New Shipment Received - {len(items)} Items ({int(total_qty)} units)"
                    from_email = os.environ.get('DEFAULT_FROM_EMAIL', 'yashraj@deyeindia.com')
                    recipient_list = ['yashraj@deyeindia.com']
                    
                    # Send email asynchronously in background thread using SendGrid API
                    import threading
                    import time
                    def _send_shipment_email():
                        try:
                            time.sleep(0.1)  # Give thread a moment to start
                            print(f"[EMAIL] 📦 Starting to send shipment email to {recipient_list}")
                            from forms.emails import send_sendgrid_email
                            success = send_sendgrid_email(recipient_list, subject, email_html, 'New shipment received')
                            if success:
                                print(f"[EMAIL] ✅ Shipment email sent for {len(items)} items via SendGrid API")
                            else:
                                print(f"[EMAIL] ⚠️ Shipment email sending had issues")
                        except Exception as email_err:
                            print(f"[EMAIL] ❌ Shipment email error: {str(email_err)}")
                            import traceback
                            traceback.print_exc()
                    
                    email_thread = threading.Thread(target=_send_shipment_email, daemon=False)
                    email_thread.start()
                    print(f"[EMAIL] 🧵 Background thread started for shipment with {len(items)} items")
                    
                except Exception as e:
                    # Log error but don't crash the app
                    print(f"Email preparation error: {str(e)}")
                
                return render(request, 'forms/update_new_shipments_confirm.html', {
                    'items': items,
                    'total_qty': total_qty,
                    'shipment_date': shipment_date,
                    'success_message': 'Shipments confirmed and saved!'
                })
            else:
                # If invalid, return to edit page with errors
                return render(request, 'forms/update_new_shipments.html', {
                    'item_formset': item_formset,
                    'empty_form': item_formset.empty_form,
                })
    else:
        item_formset = ItemFormSet(prefix='form')
    return render(request, 'forms/update_new_shipments.html', {
        'item_formset': item_formset,
        'empty_form': item_formset.empty_form,
    })
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
@login_required
@require_GET
def available_battery_serials(request):
    from django.db.models import Count
    inward_counts = InwardForm.objects.values('battery_id').annotate(count_inward=Count('id'))
    outward_counts = OutwardForm.objects.values('battery_id').annotate(count_outward=Count('id'))
    outward_map = {row['battery_id']: row['count_outward'] for row in outward_counts}
    available_serials = []
    for row in inward_counts:
        serial = row['battery_id']
        if not serial:
            continue
        inward = row['count_inward']
        outward = outward_map.get(serial, 0)
        if inward > outward:
            available_serials.append(serial)
    return JsonResponse({'serials': available_serials})
from django.views.decorators.http import require_GET
import json
from django.contrib.auth.decorators import login_required
# API endpoint for available inverter serials (inwarded but not outwarded)
@login_required
@require_GET
def available_inverter_serials(request):
    # For each inverter_id, count inward and outward occurrences
    from django.db.models import Count
    inward_counts = InwardForm.objects.values('inverter_id').annotate(count_inward=Count('id'))
    outward_counts = OutwardForm.objects.values('inverter_id_outward').annotate(count_outward=Count('id'))
    outward_map = {row['inverter_id_outward']: row['count_outward'] for row in outward_counts}
    available_serials = []
    for row in inward_counts:
        serial = row['inverter_id']
        inward = row['count_inward']
        outward = outward_map.get(serial, 0)
        if inward > outward:
            available_serials.append(serial)
    return JsonResponse({'serials': available_serials})
from django.db.models import OuterRef, Subquery, Exists
# Stock Inverters View
from .models import InwardForm, OutwardForm

from django.contrib.auth.decorators import login_required

@login_required
def stock_inverters_view(request):
    # Get all inverter_ids from OutwardForm
    outward_ids = set(OutwardForm.objects.values_list('inverter_id_outward', flat=True))
    # Get all InwardForm entries whose inverter_id is NOT in OutwardForm
    stock_inverters = InwardForm.objects.exclude(inverter_id__in=outward_ids).order_by('-created_at')
    return render(request, 'forms/stock_inverters.html', {'stock_inverters': stock_inverters})
# Simple static view for hierarchy page
from django.contrib.auth.decorators import login_required

@login_required
def hierarchy_static_view(request):
    return render(request, 'Include/hierarchy.html')
from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.urls import reverse
from datetime import date
import csv

from .models import (
    RepairingForm,
    InwardForm,
    OutwardForm,
    ServiceReportForm,
    LeaveRequest,
    UpcomingEvent,
    UserProfile,
    StockRequisition,
    DispatchedStock,
    StockItem
)

from .forms import (
    RepairingFormForm,
    InwardFormForm,
    OutwardFormForm,
    ServiceReportFormForm,
    UserRegistrationForm,
    FreightCalculatorForm,
)

from .calculator import get_all_partner_quotes, QuoteInput
from .calculator.freight_calculator import ShipmentItem
from .calculator.data_loader import load_pincode_master, lookup_pincode


# ─────────────────────────────
# HOME
# ─────────────────────────────

@login_required
def simple_home(request):
    today = date.today()
    events = UpcomingEvent.objects.filter(
        is_active=True,
        event_date__gte=today
    ).order_by('event_date')[:6]
    team_members = []
    if hasattr(request.user, 'profile'):
        team_members = request.user.profile.get_team_members()
    return render(request, 'forms/simple_home_modern.html', {'events': events, 'user': request.user, 'team_members': team_members})


@login_required
def stock_home(request):
    """Stock management home with 3 options"""
    return render(request, 'forms/stock_home.html')


@login_required
def received_stock(request):
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view received stock.")
    """Received stock dashboard with filtering"""
    from .models import StockItem
    from django.db.models import Q
    
    # Get filters from query params
    selected_year = request.GET.get('year', 'all')
    selected_component = request.GET.get('component', 'all')
    search_query = request.GET.get('search', '').strip()
    
    # Get all available years and component types
    years = StockItem.objects.values_list('year', flat=True).distinct().order_by('-year')
    all_component_types = StockItem.objects.values_list('component_type', flat=True).distinct().order_by('component_type')
    all_component_types = [ct for ct in all_component_types if ct]  # Remove empty values
    
    # Start with all items
    stock_items = StockItem.objects.all()
    
    # Apply year filter
    if selected_year != 'all':
        try:
            year_int = int(selected_year)
            stock_items = stock_items.filter(year=year_int)
        except ValueError:
            pass
    
    # Apply component type filter
    if selected_component != 'all':
        stock_items = stock_items.filter(component_type=selected_component)
    
    # Apply search filter
    if search_query:
        stock_items = stock_items.filter(
            Q(pcba_sn_new__icontains=search_query) |
            Q(pcba_sn_old__icontains=search_query) |
            Q(specification__icontains=search_query) |
            Q(remark__icontains=search_query)
        )
    
    # Get statistics
    total_items = stock_items.count()
    total_quantity = stock_items.aggregate(total=Sum('quantity'))['total'] or 0
    component_types = stock_items.values('component_type').annotate(
        count=Count('id'),
        total_qty=Sum('quantity')
    ).order_by('-count')[:10]

    # Merge duplicates by PCBA SN across all years in the filtered set
    merged = {}
    for item in stock_items.order_by('pcba_sn_new'):
        key = item.pcba_sn_new
        if key not in merged:
            merged[key] = {
                'pcba_sn_new': item.pcba_sn_new,
                'pcba_sn_old': item.pcba_sn_old,
                'component_type': item.component_type,
                'specification': item.specification,
                'quantity': item.quantity,
                'years': {item.year} if item.year else set(),
                'remark': item.remark or '',
            }
        else:
            merged[key]['quantity'] += item.quantity
            if item.pcba_sn_old and not merged[key]['pcba_sn_old']:
                merged[key]['pcba_sn_old'] = item.pcba_sn_old
            if item.component_type and not merged[key]['component_type']:
                merged[key]['component_type'] = item.component_type
            if item.specification and not merged[key]['specification']:
                merged[key]['specification'] = item.specification
            if item.remark:
                if merged[key]['remark'] and item.remark not in merged[key]['remark']:
                    merged[key]['remark'] = f"{merged[key]['remark']}; {item.remark}"
                elif not merged[key]['remark']:
                    merged[key]['remark'] = item.remark
            if item.year:
                merged[key]['years'].add(item.year)

    merged_list = list(merged.values())

    # Sort merged list by latest year desc, then component_type, then PCBA
    merged_list.sort(key=lambda x: (
        -(max(x['years']) if x['years'] else 0),
        x['component_type'] or '',
        x['pcba_sn_new']
    ))

    # Override stats to reflect merged items
    total_items = len(merged_list)
    total_quantity = sum([m['quantity'] for m in merged_list])

    # Paginate merged results
    from django.core.paginator import Paginator
    paginator = Paginator(merged_list, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'years': years,
        'selected_year': selected_year,
        'all_component_types': all_component_types,
        'selected_component': selected_component,
        'search_query': search_query,
        'stock_items': page_obj,
        'total_items': total_items,
        'total_quantity': total_quantity,
        'component_types': component_types,
    }
    return render(request, 'forms/received_stock.html', context)


@login_required
def remaining_stock(request):
    """Remaining stock view - Coming soon"""
    allowed_users = ['Nilesh', 'SnehalShinde']
    if not (request.user.is_superuser or request.user.username in allowed_users):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view remaining stock.")
    return render(request, 'forms/remaining_stock.html')


@login_required
def send_stock(request):
    """Stock requisition form (supports multiple items in one submission)."""
    try:
        from django.forms import formset_factory
        from .forms import StockRequisitionHeaderForm, StockRequisitionItemForm
        from .models import StockRequisition
        from .emails import send_bulk_requisition_email

        ItemFormSet = formset_factory(StockRequisitionItemForm, extra=1, can_delete=True)

        if request.method == 'POST':
            header_form = StockRequisitionHeaderForm(request.POST)
            item_formset = ItemFormSet(request.POST, prefix='form')

            if header_form.is_valid() and item_formset.is_valid():
                header_cd = header_form.cleaned_data
                created_requisitions = []
                
                for form in item_formset:
                    # Skip the form if it has DELETE checked
                    if form.cleaned_data.get('DELETE'):
                        continue
                    
                    # Skip the form if it's completely empty (no serial number)
                    if not form.cleaned_data.get('serial_number'):
                        continue
                    
                    # Create requisition only for forms with valid serial number
                    cd = form.cleaned_data
                    requisition = StockRequisition.objects.create(
                        serial_number=cd.get('serial_number'),
                        component_type=cd.get('component_type', ''),
                        description=cd.get('description', ''),
                        manager_name=header_cd['manager_name'],
                        quantity_required=cd.get('quantity_required') or 0,
                        required_to=header_cd['required_to'],
                        status='pending',
                    )
                    created_requisitions.append(requisition)

                created_count = len(created_requisitions)
                
                # Send consolidated email with all requisitions
                if created_requisitions:
                    try:
                        send_bulk_requisition_email(
                            created_requisitions,
                            header_cd['manager_name'],
                            header_cd['required_to']
                        )
                        print(f"✅ Email sent successfully for {created_count} requisitions")
                    except Exception as e:
                        print(f"❌ Error sending email: {str(e)}")
                        import traceback
                        traceback.print_exc()

                success_message = f'Stock requisition submitted successfully for {created_count} item(s)! Approvers have been notified.'
                # Fresh forms after successful submit
                header_form = StockRequisitionHeaderForm()
                item_formset = ItemFormSet(prefix='form')
                return render(request, 'forms/send_stock.html', {
                    'header_form': header_form,
                    'item_formset': item_formset,
                    'empty_form': item_formset.empty_form,
                    'success_message': success_message,
                })
            else:
                # Form validation failed - return with errors
                print(f"Form validation failed:")
                print(f"Header form errors: {header_form.errors}")
                print(f"Formset errors: {item_formset.errors}")
                return render(request, 'forms/send_stock.html', {
                    'header_form': header_form,
                    'item_formset': item_formset,
                    'empty_form': item_formset.empty_form,
                })
        else:
            header_form = StockRequisitionHeaderForm()
            item_formset = ItemFormSet(prefix='form')

        return render(request, 'forms/send_stock.html', {
            'header_form': header_form,
            'item_formset': item_formset,
            'empty_form': item_formset.empty_form,
        })
    except Exception as e:
        print(f"❌ CRITICAL ERROR in send_stock view: {str(e)}")
        import traceback
        traceback.print_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error: {str(e)}<br><br>Please contact support.", status=500)


@login_required
def dispatched_stock(request):
    allowed_users = ['Nilesh', 'SnehalShinde']
    if not (request.user.is_superuser or request.user.username in allowed_users):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view dispatched stock.")
    """Dispatch approved stock requisitions."""
    if request.method == 'POST':
        try:
            requisition_id = request.POST.get('requisition_id')
            if not requisition_id:
                return JsonResponse({'success': False, 'error': 'No requisition selected'})
            
            requisition = StockRequisition.objects.get(id=requisition_id)
            
            # Validate requisition is approved
            if requisition.status != 'approved':
                return JsonResponse({'success': False, 'error': 'Requisition not approved'})
            
            # Get form data
            dispatch_date = request.POST.get('dispatch_date')
            courier_name = request.POST.get('courier_name')
            tracking_number = request.POST.get('tracking_number', '')
            quantity_dispatched = int(request.POST.get('quantity_dispatched', 0))
            dispatch_remarks = request.POST.get('dispatch_remarks', '')
            
            # Validate quantity
            approved_qty = requisition.approved_quantity or requisition.quantity_required
            if quantity_dispatched > approved_qty:
                return JsonResponse({
                    'success': False, 
                    'error': f'Cannot dispatch {quantity_dispatched}. Approved quantity is {approved_qty}'
                })
            
            # Create dispatch record
            dispatch = DispatchedStock.objects.create(
                requisition=requisition,
                serial_number=requisition.serial_number,
                component_type=requisition.component_type,
                quantity_dispatched=quantity_dispatched,
                engineer_name=requisition.manager_name,
                dispatch_location=requisition.required_to,
                dispatch_date=dispatch_date,
                courier_name=courier_name,
                tracking_number=tracking_number,
                dispatch_remarks=dispatch_remarks,
                dispatched_by=request.user
            )
            
            # Update stock item quantity
            try:
                stock_item = StockItem.objects.get(pcba_sn_new=requisition.serial_number)
                stock_item.current_quantity = (stock_item.current_quantity or 0) - quantity_dispatched
                stock_item.save()
            except StockItem.DoesNotExist:
                pass
            
            # Update requisition status to dispatched if fully dispatched
            if quantity_dispatched >= approved_qty:
                requisition.status = 'dispatched'
                requisition.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Stock dispatched successfully! Tracking: {tracking_number}',
                'dispatch_id': dispatch.id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - show form
    approved_requisitions = StockRequisition.objects.filter(
        status='approved'
    ).order_by('-approval_date')
    
    return render(request, 'forms/dispatched_form.html', {
        'approved_requisitions': approved_requisitions
    })


@login_required
def stock_serial_search(request):
    """Return up to 10 matching serial suggestions from received stock."""
    from .models import StockItem
    q = (request.GET.get('q') or '').strip()
    results = []
    if q:
        qs = StockItem.objects.filter(pcba_sn_new__icontains=q).values(
            'pcba_sn_new', 'component_type', 'specification', 'year'
        ).order_by('-year')[:10]
        for row in qs:
            results.append({
                'pcba_sn_new': row['pcba_sn_new'],
                'component_type': row['component_type'] or '',
                'specification': row['specification'] or '',
                'year': row['year'] or ''
            })
    return JsonResponse({'results': results})


@login_required
def stock_serial_details(request):
    """Return details for an exact serial: latest year item, component type and specification."""
    from .models import StockItem
    sn = (request.GET.get('sn') or '').strip()
    if not sn:
        return JsonResponse({'found': False})
    item = StockItem.objects.filter(pcba_sn_new=sn).order_by('-year').first()
    if not item:
        return JsonResponse({'found': False})
    return JsonResponse({
        'found': True,
        'pcba_sn_new': item.pcba_sn_new,
        'component_type': item.component_type or '',
        'specification': item.specification or '',
        'year': item.year,
        'quantity': float(item.quantity) if item.quantity is not None else 0
    })


@login_required
def stock_info_api(request):
    """Return stock info for a requisition ID."""
    req_id = request.GET.get('requisition_id')
    if not req_id:
        return JsonResponse({'success': False, 'error': 'No requisition ID provided'})
    
    try:
        requisition = StockRequisition.objects.get(id=req_id)
        
        # Get current stock
        current_stock = 0
        try:
            stock_item = StockItem.objects.get(pcba_sn_new=requisition.serial_number)
            current_stock = stock_item.current_quantity or 0
        except StockItem.DoesNotExist:
            pass
        
        # Calculate quantities
        approved_qty = requisition.approved_quantity or requisition.quantity_required
        remaining = current_stock - approved_qty
        
        return JsonResponse({
            'success': True,
            'serial_number': requisition.serial_number,
            'component_type': requisition.component_type,
            'engineer_name': requisition.manager_name,
            'dispatch_location': requisition.required_to,
            'quantity_approved': approved_qty,
            'current_stock': current_stock,
            'remaining_stock': remaining,
            'approved_by': requisition.approved_by or '',
            'approval_date': requisition.approval_date.strftime('%Y-%m-%d') if requisition.approval_date else ''
        })
    except StockRequisition.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Requisition not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─────────────────────────────
# FORMS DASHBOARD
# ─────────────────────────────

@login_required
def select_form_page(request):
    return render(request, 'forms/select_form.html')


@login_required
def forms_data_overview(request):
    context = {
        'inwards': InwardForm.objects.order_by('-created_at')[:50],
        'outwards': OutwardForm.objects.order_by('-created_at')[:50],
        'service_reports': ServiceReportForm.objects.order_by('-created_at')[:50],
        'repairs': RepairingForm.objects.order_by('-created_at')[:50],
    }
    return render(request, 'forms/data_overview.html', context)


@login_required
def repairing_form_page(request):
    if request.method == 'POST':
        print('\n[RepairingForm] ===== POST DATA RECEIVED =====')
        print(f'All POST keys: {list(request.POST.keys())}')
        print(f'Full POST data: {dict(request.POST.lists())}')
        
        # Template uses 'Tested_by' instead of 'tested_by'
        data = request.POST.copy()
        if 'Tested_by' in data and 'tested_by' not in data:
            data['tested_by'] = data.get('Tested_by')

        form = RepairingFormForm(data)
        if form.is_valid():
            print(f'[RepairingForm] Form valid. Cleaned data keys: {list(form.cleaned_data.keys())}')
            instance = form.save(commit=False)
            # Collect multiple checkbox values for fault_problems
            problems = request.POST.getlist('fault_problems')
            instance.fault_problems = problems if problems else []
            print(f'[RepairingForm] Fault problems captured: {instance.fault_problems}')
            instance.user = request.user
            instance.save()
            print(f'[RepairingForm] ✓ Saved successfully. ID: {instance.id}')
            return redirect(f"{request.path}?success=1")
        else:
            print('[RepairingForm] Validation errors:', form.errors.as_json())
            return render(request, 'forms/repairing_form.html', {
                'form': form,
                'success': False,
                'form_errors': form.errors,
            })
    else:
        form = RepairingFormForm()
        return render(request, 'forms/repairing_form.html', {'form': form})


@login_required
def inward_form_page(request):
    if request.method == 'POST':
        print('\n[InwardForm] ===== POST DATA RECEIVED =====')
        print(f'All POST keys: {list(request.POST.keys())}')
        print(f'Full POST data: {dict(request.POST.lists())}')
        
        form = InwardFormForm(request.POST)
        if form.is_valid():
            print(f'[InwardForm] Form valid. Cleaned data keys: {list(form.cleaned_data.keys())}')
            print(f'[InwardForm] Accessories: {form.cleaned_data.get("accessories")}')
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            print(f'[InwardForm] ✓ Saved successfully. ID: {instance.id}')
            return redirect(f"{request.path}?success=1")
        # Log errors to console for debugging
        print('[InwardForm] Validation errors:', form.errors.as_json())
        return render(request, 'forms/inward_form.html', {
            'form': form,
            'success': False,
            'form_errors': form.errors,
        })
    form = InwardFormForm()
    return render(request, 'forms/inward_form.html', {'form': form})


@login_required
def outward_form_page(request):
    # For each inverter_id, count inward and outward occurrences
    from django.db.models import Count
    inward_counts = InwardForm.objects.values('inverter_id').annotate(count_inward=Count('id'))
    outward_counts = OutwardForm.objects.values('inverter_id_outward').annotate(count_outward=Count('id'))
    outward_map = {row['inverter_id_outward']: row['count_outward'] for row in outward_counts}
    available_serials = []
    for row in inward_counts:
        serial = row['inverter_id']
        inward = row['count_inward']
        outward = outward_map.get(serial, 0)
        if inward > outward:
            available_serials.append(serial)
    if request.method == 'POST':
        print('\n[OutwardForm] ===== POST DATA RECEIVED =====')
        print(f'All POST keys: {list(request.POST.keys())}')
        print(f'Full POST data: {dict(request.POST.lists())}')
        
        form = OutwardFormForm(request.POST)
        if form.is_valid():
            print(f'[OutwardForm] Form valid. Cleaned data keys: {list(form.cleaned_data.keys())}')
            print(f'[OutwardForm] Accessories: {form.cleaned_data.get("accessories")}')
            print(f'[OutwardForm] Control card changed: {form.cleaned_data.get("control_card_changed")}')
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            print(f'[OutwardForm] ✓ Saved successfully. ID: {instance.id}')
            return redirect(f"{request.path}?success=1")
        print('[OutwardForm] Validation errors:', form.errors.as_json())
        return render(request, 'forms/outward_form.html', {
            'form': form,
            'success': False,
            'form_errors': form.errors,
            'available_serials': available_serials,
        })
    form = OutwardFormForm()
    return render(request, 'forms/outward_form.html', {'form': form, 'available_serials': available_serials})


@login_required
def service_form_page(request):
    if request.method == 'POST':
        print('\n[ServiceReportForm] ===== POST DATA RECEIVED =====')
        print(f'All POST keys: {list(request.POST.keys())}')
        print(f'Full POST data: {dict(request.POST.lists())}')
        
        data = request.POST.copy()
        # Map signature hidden inputs to model fields if present
        eng_sig = data.get('engData')
        cust_sig = data.get('custData')
        print(f'[ServiceReportForm] Engineer signature data present: {bool(eng_sig)}')
        print(f'[ServiceReportForm] Customer signature data present: {bool(cust_sig)}')
        
        form = ServiceReportFormForm(data)
        if form.is_valid():
            print(f'[ServiceReportForm] Form valid. Cleaned data keys: {list(form.cleaned_data.keys())}')
            instance = form.save(commit=False)
            instance.user = request.user
            if eng_sig:
                instance.engineer_signature_data = eng_sig
            if cust_sig:
                instance.customer_signature_data = cust_sig
            
            # Parse PV data from POST parameters (pv1_voltage, pv1_current, etc.)
            pv_data = []
            for i in range(1, 9):  # PV 1-8
                pv_entry = {
                    'voltage': data.get(f'pv{i}_voltage', ''),
                    'current': data.get(f'pv{i}_current', ''),
                    'earthing': data.get(f'pv{i}_earthing', ''),
                    'panel': data.get(f'pv{i}_panel', ''),
                    'observation': data.get(f'pv{i}_observation', ''),
                }
                pv_data.append(pv_entry)
            instance.pv_data = pv_data
            print(f'[ServiceReportForm] PV data captured: {instance.pv_data}')
            
            # Parse AC data from POST parameters (ac_rn_voltage, ac_yn_voltage, etc.)
            ac_data = {
                'R-N': {
                    'voltage': data.get('ac_rn_voltage', ''),
                    'current': data.get('ac_rn_current', ''),
                    'earthing': data.get('ac_rn_earthing', ''),
                },
                'Y-N': {
                    'voltage': data.get('ac_yn_voltage', ''),
                    'current': data.get('ac_yn_current', ''),
                    'earthing': data.get('ac_yn_earthing', ''),
                },
                'B-N': {
                    'voltage': data.get('ac_bn_voltage', ''),
                    'current': data.get('ac_bn_current', ''),
                    'earthing': data.get('ac_bn_earthing', ''),
                },
                'R-Y': {
                    'voltage': data.get('ac_ry_voltage', ''),
                    'current': data.get('ac_ry_current', ''),
                    'earthing': data.get('ac_ry_earthing', ''),
                },
                'Y-B': {
                    'voltage': data.get('ac_yb_voltage', ''),
                    'current': data.get('ac_yb_current', ''),
                    'earthing': data.get('ac_yb_earthing', ''),
                },
                'B-R': {
                    'voltage': data.get('ac_br_voltage', ''),
                    'current': data.get('ac_br_current', ''),
                    'earthing': data.get('ac_br_earthing', ''),
                },
                'N-PE': {
                    'voltage': data.get('ac_npe_voltage', ''),
                    'current': data.get('ac_npe_current', ''),
                    'earthing': data.get('ac_npe_earthing', ''),
                },
            }
            instance.ac_data = ac_data
            print(f'[ServiceReportForm] AC data captured: {instance.ac_data}')
            
            instance.save()
            print(f'[ServiceReportForm] ✓ Saved successfully. ID: {instance.id}')
            return redirect(f"{request.path}?success=1")
        print('[ServiceReportForm] Validation errors:', form.errors.as_json())
        return render(request, 'forms/service_form.html', {
            'form': form,
            'success': False,
            'form_errors': form.errors,
        })
    form = ServiceReportFormForm()
    return render(request, 'forms/service_form.html', {'form': form})


@login_required
def hierarchy_details(request):
    # Minimal hierarchy logic only
    from collections import defaultdict
    from .models import UserProfile
    profiles = UserProfile.objects.select_related('user', 'manager').all()
    manager_map = defaultdict(list)
    for profile in profiles:
        if profile.manager:
            manager_map[profile.manager.id].append(profile)
    top_level = [profile for profile in profiles if profile.manager is None]
    context = {
        'top_level': top_level,
        'manager_map': manager_map,
    }
    return render(request, 'Include/hierarchy.html', context)


# ─────────────────────────────
# FREIGHT CALCULATOR
# ─────────────────────────────

@login_required
def freight_calculator(request):
    results = None
    error = None
    missing_pincodes = []
    
    if request.method == 'POST':
        form = FreightCalculatorForm(request.POST)
        
        # DEBUG: Log all POST data received
        print("=" * 80)
        print("FREIGHT CALCULATOR - POST DATA RECEIVED:")
        print("=" * 80)
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                print(f"  {key}: {value}")
        print("=" * 80)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # DEBUG: Log cleaned data
            print("\nCLEANED FORM DATA:")
            print("-" * 80)
            for key, value in data.items():
                print(f"  {key}: {value}")
            print("-" * 80)
            
            # Build items list from form data (multiple items support)
            items = []
            item_index = 0
            while True:
                weight_key = f'weight_kg_{item_index}' if item_index > 0 else 'weight_kg'
                length_key = f'length_cm_{item_index}' if item_index > 0 else 'length_cm'
                breadth_key = f'breadth_cm_{item_index}' if item_index > 0 else 'breadth_cm'
                height_key = f'height_cm_{item_index}' if item_index > 0 else 'height_cm'
                
                # Check if this item exists in POST data
                if weight_key in request.POST or (item_index == 0 and 'weight_kg' in data):
                    weight = float(request.POST.get(weight_key, data.get('weight_kg', 0)))
                    length = float(request.POST.get(length_key, data.get('length_cm', 0)))
                    breadth = float(request.POST.get(breadth_key, data.get('breadth_cm', 0)))
                    height = float(request.POST.get(height_key, data.get('height_cm', 0)))
                    
                    print(f"\nITEM {item_index}: weight={weight}kg, L={length}cm, B={breadth}cm, H={height}cm")
                    
                    if weight > 0 and length > 0 and breadth > 0 and height > 0:
                        items.append(ShipmentItem(
                            weight_kg=weight,
                            length_cm=length,
                            breadth_cm=breadth,
                            height_cm=height,
                        ))
                    item_index += 1
                else:
                    break
            
            print(f"\nTOTAL ITEMS CREATED: {len(items)}")
            print("=" * 80)
            
            # If no items were added, create one from main form fields
            if not items:
                items = [ShipmentItem(
                    weight_kg=data['weight_kg'],
                    length_cm=data['length_cm'],
                    breadth_cm=data['breadth_cm'],
                    height_cm=data['height_cm'],
                )]
            
            q = QuoteInput(
                from_pincode=data['from_pincode'],
                to_pincode=data['to_pincode'],
                items=items,
                reverse_pickup=data.get('reverse_pickup') or False,
                insured_value=data.get('insured_value') or 0.0,
                days_in_transit_storage=data.get('days_in_transit_storage') or 0,
                gst_mode=data.get('gst_mode', '12pct'),
            )
            try:
                # Check if pincodes exist in database
                import pathlib
                from forms.calculator.data_loader import load_pincode_master
                base_dir = str(pathlib.Path(__file__).resolve().parents[2])
                pins_db = load_pincode_master(base_dir)
                
                if data['from_pincode'] not in pins_db:
                    missing_pincodes.append(f"From Pincode: {data['from_pincode']}")
                if data['to_pincode'] not in pins_db:
                    missing_pincodes.append(f"To Pincode: {data['to_pincode']}")
                
                results = get_all_partner_quotes(q)
                # Normalize surcharge keys so template lookups never fail
                for r in results or []:
                    if hasattr(r, 'surcharges') and isinstance(r.surcharges, dict):
                        for k in ['waybill', 'docket', 'fuel_surcharge', 'oda', 'metro_charge', 'insurance', 'valuation', 'reverse_pickup', 'handling', 'demurrage']:
                            r.surcharges.setdefault(k, 0.0)
            except Exception as exc:
                error = f"Calculator error: {exc}"
                print(f"\n❌ CALCULATOR ERROR: {exc}")
                print("=" * 80)
        else:
            error = 'Please correct the errors below.'
            print("\n❌ FORM VALIDATION ERRORS:")
            print("-" * 80)
            for field, errors in form.errors.items():
                print(f"  {field}: {', '.join(errors)}")
            print("=" * 80)
    else:
        form = FreightCalculatorForm()

    return render(request, 'forms/freight_calculator.html', {
        'form': form,
        'results': results,
        'error': error,
        'missing_pincodes': missing_pincodes,
    })


@login_required
def pincode_lookup_api(request):
    pin = request.GET.get('pin') or request.GET.get('pincode')
    if not pin:
        return JsonResponse({'ok': False, 'error': 'pin required'}, status=400)
    try:
        import pathlib
        base_dir = str(pathlib.Path(__file__).resolve().parents[2])
        db = load_pincode_master(base_dir)
        rec = lookup_pincode(db, str(pin))
        if not rec:
            return JsonResponse({'ok': False, 'error': 'not found'}, status=404)
        data = {
            'pincode': rec.pincode,
            'city': rec.city,
            'state': rec.state,
            'metro': bool(rec.is_metro) if rec.is_metro is not None else None,
            'oda': bool(rec.is_oda) if rec.is_oda is not None else None,
            'safexpress_zone': rec.safexpress_zone,
            'bluedart_region': rec.bluedart_region,
            'global_cargo_region': rec.global_cargo_region,
        }
        return JsonResponse({'ok': True, 'data': data})
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)

# ─────────────────────────────
# LEAVE MANAGEMENT
# ─────────────────────────────

@login_required
def leave_home(request):
    return render(request, 'leave/leave_home.html')


@login_required
def apply_leave(request):
    def _remaining_paid_leave(user, year):
        # Only count APPROVED leaves towards used balance
        used = LeaveRequest.objects.filter(
            user=user,
            leave_type='leave',
            start_date__year=year,
            status='approved'  # Only approved leaves deduct from balance
        ).aggregate(total=Sum('total_days'))['total'] or 0.0
        return max(21.0 - used, 0.0)

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_breakdown = request.POST.get('start_breakdown', 'full')
        end_breakdown = request.POST.get('end_breakdown', 'full')
        reason = request.POST.get('reason', '')

        # Coerce dates early for validation and balance checks
        try:
            sd = date.fromisoformat(start_date)
            ed = date.fromisoformat(end_date)
        except Exception:
            return render(request, 'leave/apply_leave.html', {
                'error': 'Invalid dates provided.',
                'success': False,
            })

        lr = LeaveRequest(
            user=request.user,
            leave_type=leave_type,
            start_date=sd,
            end_date=ed,
            start_breakdown=start_breakdown,
            end_breakdown=end_breakdown,
            reason=reason,
            status='pending'
        )

        requested_days = lr.compute_total_days()

        if requested_days <= 0:
            return render(request, 'leave/apply_leave.html', {
                'error': 'Requested leave days calculate to zero. Please adjust dates (Sundays are excluded).',
                'success': False,
            })

        remaining = _remaining_paid_leave(request.user, sd.year)
        if leave_type == 'leave' and requested_days > remaining:
            return render(request, 'leave/apply_leave.html', {
                'error': f'Insufficient balance. Remaining paid leave: {remaining:.1f} days. Requested: {requested_days:.1f} days.',
                'success': False,
            })

        # Persist after validation
        lr.save()

        # Send email notification with approve/reject links
        approve_url = request.build_absolute_uri(
            reverse('forms:approve_leave_email', kwargs={'leave_id': lr.id})
        )
        reject_url = request.build_absolute_uri(
            reverse('forms:reject_leave_email', kwargs={'leave_id': lr.id})
        )
        
        email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }}
                h2 {{ color: #2c3e50; margin-bottom: 20px; }}
                .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ color: #333; margin-left: 10px; }}
                .actions {{ margin-top: 30px; text-align: center; }}
                .btn {{ display: inline-block; padding: 12px 30px; margin: 10px; text-decoration: none; 
                       border-radius: 5px; font-weight: bold; color: white; }}
                .btn-approve {{ background: #27ae60; }}
                .btn-approve:hover {{ background: #229954; }}
                .btn-reject {{ background: #e74c3c; }}
                .btn-reject:hover {{ background: #c0392b; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 2px solid #eee; 
                          text-align: center; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🔔 New Leave Request</h2>
                
                <div class="detail-row">
                    <span class="label">Employee:</span>
                    <span class="value">{request.user.get_full_name() or request.user.username}</span>
                </div>
                
                <div class="detail-row">
                    <span class="label">Request Type:</span>
                    <span class="value">{lr.get_leave_type_display()}</span>
                </div>
                
                <div class="detail-row">
                    <span class="label">Start Date:</span>
                    <span class="value">{lr.start_date.strftime('%d %b %Y')} ({lr.get_start_breakdown_display()})</span>
                </div>
                
                <div class="detail-row">
                    <span class="label">End Date:</span>
                    <span class="value">{lr.end_date.strftime('%d %b %Y')} ({lr.get_end_breakdown_display()})</span>
                </div>
                
                <div class="detail-row">
                    <span class="label">Total Days:</span>
                    <span class="value">{lr.total_days} day(s)</span>
                </div>
                
                <div class="detail-row">
                    <span class="label">Reason:</span>
                    <span class="value">{lr.reason or 'No reason provided'}</span>
                </div>
                
                <div class="actions">
                    <a href="{approve_url}" class="btn btn-approve">✓ APPROVE</a>
                    <a href="{reject_url}" class="btn btn-reject">✗ REJECT</a>
                </div>
                
                <div class="footer">
                    This is an automated notification from Deye Leave Management System.<br>
                    Click the buttons above to approve or reject this request.
                </div>
            </div>
        </body>
        </html>
        """
        
        email_text = f"""
New Leave Request

Employee: {request.user.get_full_name() or request.user.username}
Type: {lr.get_leave_type_display()}
Start Date: {lr.start_date.strftime('%d %b %Y')} ({lr.get_start_breakdown_display()})
End Date: {lr.end_date.strftime('%d %b %Y')} ({lr.get_end_breakdown_display()})
Total Days: {lr.total_days}
Reason: {lr.reason or 'No reason provided'}

Approve: {approve_url}
Reject: {reject_url}
        """
        
        # Send email to HR and manager via SendGrid (non-blocking)
        try:
            msg = EmailMultiAlternatives(
                subject=f'New {lr.get_leave_type_display()} Request - {request.user.get_full_name() or request.user.username}',
                body=email_text,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'yashraj@deyeindia.com'),
                to=['hr@deyeindia.com', 'yashraj@deyeindia.com']
            )
            msg.attach_alternative(email_html, "text/html")
            msg.send(fail_silently=True)
            print(f"✅ Leave request email sent for {lr.user.username}")
        except Exception as e:
            # Log error but don't crash - leave request is already saved
            print(f"⚠️ Email send failed (non-critical): {str(e)}")

        return redirect(f"{request.path}?success=1")
    else:
        success = request.GET.get('success') == '1'
        # Show remaining balance for current year
        today = date.today()
        remaining = _remaining_paid_leave(request.user, today.year)
        return render(request, 'leave/apply_leave.html', {'success': success, 'remaining': remaining})


@login_required
def leave_status(request):
    leaves = LeaveRequest.objects.filter(user=request.user).order_by('-id')
    return render(request, 'leave/leave_status.html', {'leaves': leaves})


@login_required
def leave_history(request):
    def _remaining_paid_leave(user, year):
        # Only count APPROVED leaves towards used balance
        used = LeaveRequest.objects.filter(
            user=user,
            leave_type='leave',
            start_date__year=year,
            status='approved'  # Only approved leaves deduct from balance
        ).aggregate(total=Sum('total_days'))['total'] or 0.0
        return max(21.0 - used, 0.0)

    leaves = LeaveRequest.objects.filter(
        user=request.user
    ).exclude(status='pending').order_by('-id')

    today = date.today()
    remaining = _remaining_paid_leave(request.user, today.year)

    return render(request, 'leave/leave_history.html', {
        'leaves': leaves,
        'remaining_leave': remaining,
        'current_year': today.year,
    })


# ─────────────────────────────
# ADMIN LEAVE MANAGEMENT
# ─────────────────────────────

def _is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(_is_admin)
def leave_admin(request):
    leaves = LeaveRequest.objects.select_related('user', 'status_changed_by').order_by('-applied_at')
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')

    if status_filter:
        leaves = leaves.filter(status=status_filter)
    if type_filter:
        leaves = leaves.filter(leave_type=type_filter)

    return render(request, 'leave/admin_leave_list.html', {
        'leaves': leaves,
        'status_filter': status_filter or '',
        'type_filter': type_filter or '',
    })


@login_required
@user_passes_test(_is_admin)
def update_leave_status(request, leave_id):
    if request.method != 'POST':
        return HttpResponseForbidden('Invalid method')

    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    new_status = request.POST.get('status')
    if new_status not in dict(LeaveRequest.LEAVE_STATUS_CHOICES):
        return HttpResponseForbidden('Invalid status')

    leave.status = new_status
    leave.status_changed_at = timezone.now()
    if request.user.is_authenticated:
        leave.status_changed_by = request.user
    leave.save()

    # Send status update email (fail silently to avoid blocking the update)
    if leave.user.email:
        try:
            send_mail(
                subject='Leave status updated',
                message=(
                    f"Hello {leave.user.get_username()},\n\n"
                    f"Your leave request from {leave.start_date} to {leave.end_date} is now {leave.status.title()}.\n"
                    f"Total days: {leave.total_days}."
                ),
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[leave.user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email error (non-critical): {e}")
    
    return redirect('forms:leave_admin')


@login_required
@user_passes_test(_is_admin)
def leave_export_csv(request):
    leaves = LeaveRequest.objects.select_related('user', 'status_changed_by').order_by('-applied_at')
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')

    if status_filter:
        leaves = leaves.filter(status=status_filter)
    if type_filter:
        leaves = leaves.filter(leave_type=type_filter)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leave_requests.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Employee', 'Type', 'Start', 'End', 'Start Portion', 'End Portion',
        'Total Days', 'Status', 'Applied At', 'Status Changed At', 'Changed By', 'Reason'
    ])
    for leave in leaves:
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


@login_required
@user_passes_test(_is_admin)
def leave_admin_report(request):
    """
    Employee-wise leave statistics report.
    Shows per-employee: total requests, approved, rejected, taken, remaining.
    """
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
            'total_approved': total_approved,
            'total_rejected': total_rejected,
            'total_taken': total_taken,
            'remaining': remaining,
        })

    return render(request, 'leave/admin_leave_report.html', {
        'report_data': report_data,
        'current_year': current_year,
    })


def approve_leave_email(request, leave_id):
    """
    Handle leave approval via email link.
    """
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    
    if leave.status != 'pending':
        return render(request, 'leave/email_action_result.html', {
            'success': False,
            'message': f'This leave request has already been {leave.status}.',
            'leave': leave
        })
    
    leave.status = 'approved'
    leave.status_changed_at = timezone.now()
    leave.status_changed_by = None  # Email action, no specific user
    leave.save()
    
    # Send confirmation email to employee
    try:
        employee_email = leave.user.email
        if employee_email:
            send_mail(
                subject=f'Leave Request Approved - {leave.start_date.strftime("%d %b %Y")}',
                message=f"""
Dear {leave.user.get_full_name() or leave.user.username},

Your leave request has been APPROVED.

Details:
- Type: {leave.get_leave_type_display()}
- Start Date: {leave.start_date.strftime('%d %b %Y')} ({leave.get_start_breakdown_display()})
- End Date: {leave.end_date.strftime('%d %b %Y')} ({leave.get_end_breakdown_display()})
- Total Days: {leave.total_days}

Regards,
Deye India HR Team
                """,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@deyeindia.com'),
                recipient_list=[employee_email],
                fail_silently=True,
            )
    except:
        pass
    
    return render(request, 'leave/email_action_result.html', {
        'success': True,
        'action': 'approved',
        'message': 'Leave request has been successfully approved!',
        'leave': leave
    })


def reject_leave_email(request, leave_id):
    """
    Handle leave rejection via email link.
    """
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    
    if leave.status != 'pending':
        return render(request, 'leave/email_action_result.html', {
            'success': False,
            'message': f'This leave request has already been {leave.status}.',
            'leave': leave
        })
    
    leave.status = 'rejected'
    leave.status_changed_at = timezone.now()
    leave.status_changed_by = None  # Email action, no specific user
    leave.save()
    
    # Send confirmation email to employee
    try:
        employee_email = leave.user.email
        if employee_email:
            send_mail(
                subject=f'Leave Request Rejected - {leave.start_date.strftime("%d %b %Y")}',
                message=f"""
Dear {leave.user.get_full_name() or leave.user.username},

Your leave request has been REJECTED.

Details:
- Type: {leave.get_leave_type_display()}
- Start Date: {leave.start_date.strftime('%d %b %Y')} ({leave.get_start_breakdown_display()})
- End Date: {leave.end_date.strftime('%d %b %Y')} ({leave.get_end_breakdown_display()})
- Total Days: {leave.total_days}

Please contact HR for more information.

Regards,
Deye India HR Team
                """,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@deyeindia.com'),
                recipient_list=[employee_email],
                fail_silently=True,
            )
    except:
        pass
    
    return render(request, 'leave/email_action_result.html', {
        'success': True,
        'action': 'rejected',
        'message': 'Leave request has been rejected.',
        'leave': leave
    })


# ─────────────────────────────
# USER REGISTRATION
# ─────────────────────────────

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create UserProfile with date of birth
            UserProfile.objects.create(
                user=user,
                date_of_birth=form.cleaned_data.get('date_of_birth'),
                phone=form.cleaned_data.get('phone', ''),
                department=form.cleaned_data.get('department', '')
            )
            
            # Auto-login after registration
            login(request, user)
            return redirect('forms:simple_home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def birthday_greeting(request, user_id):
    """Display birthday greeting with fireworks animation"""
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)
    return render(request, 'birthday/birthday_greeting.html', {'user': user})


# ─────────────────────────────
# EMPLOYEE DATA DASHBOARD
# ─────────────────────────────

@login_required
def employee_data_view(request):
    """Display all form responses submitted by the logged-in employee with filters"""
    from datetime import datetime, timedelta
    
    user = request.user
    user_name = user.get_full_name() or user.username
    user_email = user.email
    
    # Get tab-specific filter parameters
    repairing_date_from = request.GET.get('repairing_date_from', '')
    repairing_date_to = request.GET.get('repairing_date_to', '')
    repairing_search = request.GET.get('repairing_search', '')
    
    inward_date_from = request.GET.get('inward_date_from', '')
    inward_date_to = request.GET.get('inward_date_to', '')
    inward_search = request.GET.get('inward_search', '')
    
    outward_date_from = request.GET.get('outward_date_from', '')
    outward_date_to = request.GET.get('outward_date_to', '')
    outward_search = request.GET.get('outward_search', '')
    
    service_date_from = request.GET.get('service_date_from', '')
    service_date_to = request.GET.get('service_date_to', '')
    service_search = request.GET.get('service_search', '')
    
    stock_req_date_from = request.GET.get('stock_req_date_from', '')
    stock_req_date_to = request.GET.get('stock_req_date_to', '')
    stock_req_search = request.GET.get('stock_req_search', '')
    stock_req_status = request.GET.get('stock_req_status', '')
    
    stock_disp_date_from = request.GET.get('stock_disp_date_from', '')
    stock_disp_date_to = request.GET.get('stock_disp_date_to', '')
    stock_disp_search = request.GET.get('stock_disp_search', '')
    
    # Repairing Forms (show only forms filled by the logged-in user)
    repairing_forms = RepairingForm.objects.filter(user=user)
    if repairing_date_from:
        from_date = datetime.strptime(repairing_date_from, '%Y-%m-%d')
        repairing_forms = repairing_forms.filter(created_at__gte=from_date)
    if repairing_date_to:
        to_date = datetime.strptime(repairing_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        repairing_forms = repairing_forms.filter(created_at__lt=end_date)
    if repairing_search:
        repairing_forms = repairing_forms.filter(
            Q(case_number__icontains=repairing_search) |
            Q(customer_abbrev__icontains=repairing_search) |
            Q(inverter_id__icontains=repairing_search)
        )
    repairing_forms = repairing_forms.order_by('-created_at')
    
    # Inward Forms (show only forms filled by the logged-in user)
    inward_forms = InwardForm.objects.filter(user=user)
    if inward_date_from:
        from_date = datetime.strptime(inward_date_from, '%Y-%m-%d')
        inward_forms = inward_forms.filter(created_at__gte=from_date)
    if inward_date_to:
        to_date = datetime.strptime(inward_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        inward_forms = inward_forms.filter(created_at__lt=end_date)
    if inward_search:
        inward_forms = inward_forms.filter(
            Q(customer_name__icontains=inward_search) |
            Q(inverter_id__icontains=inward_search) |
            Q(awb_lr_number__icontains=inward_search)
        )
    inward_forms = inward_forms.order_by('-created_at')
    
    # Outward Forms (show only forms filled by the logged-in user)
    outward_forms = OutwardForm.objects.filter(user=user)
    if outward_date_from:
        from_date = datetime.strptime(outward_date_from, '%Y-%m-%d')
        outward_forms = outward_forms.filter(created_at__gte=from_date)
    if outward_date_to:
        to_date = datetime.strptime(outward_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        outward_forms = outward_forms.filter(created_at__lt=end_date)
    if outward_search:
        outward_forms = outward_forms.filter(
            Q(inverter_id_outward__icontains=outward_search) |
            Q(sent_to_company__icontains=outward_search) |
            Q(awb_number__icontains=outward_search)
        )
    outward_forms = outward_forms.order_by('-created_at')
    
    # Service Report Forms (show only forms filled by the logged-in user)
    service_forms = ServiceReportForm.objects.filter(
        Q(user=user) |
        Q(email=user_email) |
        Q(engineer_first_name__icontains=user.first_name, engineer_last_name__icontains=user.last_name)
    )
    if service_date_from:
        from_date = datetime.strptime(service_date_from, '%Y-%m-%d')
        service_forms = service_forms.filter(created_at__gte=from_date)
    if service_date_to:
        to_date = datetime.strptime(service_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        service_forms = service_forms.filter(created_at__lt=end_date)
    if service_search:
        service_forms = service_forms.filter(
            Q(serial_number__icontains=service_search) |
            Q(customer_first_name__icontains=service_search) |
            Q(customer_last_name__icontains=service_search)
        )
    service_forms = service_forms.order_by('-created_at')
    
    # Stock Requisitions (show only forms filled by the logged-in user)
    stock_requisitions = StockRequisition.objects.filter(user=user)
    if stock_req_date_from:
        from_date = datetime.strptime(stock_req_date_from, '%Y-%m-%d')
        stock_requisitions = stock_requisitions.filter(created_at__gte=from_date)
    if stock_req_date_to:
        to_date = datetime.strptime(stock_req_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        stock_requisitions = stock_requisitions.filter(created_at__lt=end_date)
    if stock_req_search:
        stock_requisitions = stock_requisitions.filter(
            Q(serial_number__icontains=stock_req_search) |
            Q(component_type__icontains=stock_req_search) |
            Q(description__icontains=stock_req_search)
        )
    if stock_req_status:
        stock_requisitions = stock_requisitions.filter(status=stock_req_status)
    stock_requisitions = stock_requisitions.order_by('-created_at')
    
    # Dispatched Stock
    # Dispatched Stock (show only forms filled by the logged-in user)
    dispatched_stock = DispatchedStock.objects.filter(user=user)
    if stock_disp_date_from:
        from_date = datetime.strptime(stock_disp_date_from, '%Y-%m-%d')
        dispatched_stock = dispatched_stock.filter(created_at__gte=from_date)
    if stock_disp_date_to:
        to_date = datetime.strptime(stock_disp_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        dispatched_stock = dispatched_stock.filter(created_at__lt=end_date)
    if stock_disp_search:
        dispatched_stock = dispatched_stock.filter(
            Q(serial_number__icontains=stock_disp_search) |
            Q(component_type__icontains=stock_disp_search) |
            Q(tracking_number__icontains=stock_disp_search)
        )
    dispatched_stock = dispatched_stock.order_by('-created_at')
    
    # Calculate duplicate serial numbers PER FORM TYPE (not across all forms)
    from collections import Counter
    
    # Count duplicates separately for each form type (excluding stock forms)
    # Build counters by object type for each form
    repairing_inv = Counter(f.inverter_id for f in repairing_forms if f.repairing_object == 'Inverter' and f.inverter_id)
    repairing_bat = Counter(f.battery_id for f in repairing_forms if f.repairing_object == 'Battery' and f.battery_id)
    repairing_pcb = Counter(f.pcb_serial_number for f in repairing_forms if f.repairing_object == 'PCB' and f.pcb_serial_number)

    inward_inv = Counter(f.inverter_id for f in inward_forms if f.inward_object == 'Inverter' and f.inverter_id)
    inward_bat = Counter(f.battery_id for f in inward_forms if f.inward_object == 'Battery' and f.battery_id)
    inward_pcb = Counter(f.pcb_serial_number for f in inward_forms if f.inward_object == 'PCB' and f.pcb_serial_number)

    outward_inv = Counter(f.inverter_id_outward for f in outward_forms if f.outward_object == 'Inverter' and f.inverter_id_outward)
    outward_bat = Counter(f.battery_id for f in outward_forms if f.outward_object == 'Battery' and f.battery_id)
    outward_pcb = Counter(f.pcb_serial_number for f in outward_forms if f.outward_object == 'PCB' and f.pcb_serial_number)

    service_serials = Counter(service_forms.values_list('serial_number', flat=True))

    # Annotate each object with duplicate count (only within its own form type/object type)
    for form in repairing_forms:
        if form.repairing_object == 'Inverter':
            form.duplicate_count = repairing_inv.get(form.inverter_id, 0) if repairing_inv.get(form.inverter_id, 0) > 1 else 0
        elif form.repairing_object == 'Battery':
            form.duplicate_count = repairing_bat.get(form.battery_id, 0) if repairing_bat.get(form.battery_id, 0) > 1 else 0
        elif form.repairing_object == 'PCB':
            form.duplicate_count = repairing_pcb.get(form.pcb_serial_number, 0) if repairing_pcb.get(form.pcb_serial_number, 0) > 1 else 0
        else:
            form.duplicate_count = 0

    for form in inward_forms:
        if form.inward_object == 'Inverter':
            form.duplicate_count = inward_inv.get(form.inverter_id, 0) if inward_inv.get(form.inverter_id, 0) > 1 else 0
        elif form.inward_object == 'Battery':
            form.duplicate_count = inward_bat.get(form.battery_id, 0) if inward_bat.get(form.battery_id, 0) > 1 else 0
        elif form.inward_object == 'PCB':
            form.duplicate_count = inward_pcb.get(form.pcb_serial_number, 0) if inward_pcb.get(form.pcb_serial_number, 0) > 1 else 0
        else:
            form.duplicate_count = 0

    for form in outward_forms:
        if form.outward_object == 'Inverter':
            form.duplicate_count = outward_inv.get(form.inverter_id_outward, 0) if outward_inv.get(form.inverter_id_outward, 0) > 1 else 0
        elif form.outward_object == 'Battery':
            form.duplicate_count = outward_bat.get(form.battery_id, 0) if outward_bat.get(form.battery_id, 0) > 1 else 0
        elif form.outward_object == 'PCB':
            form.duplicate_count = outward_pcb.get(form.pcb_serial_number, 0) if outward_pcb.get(form.pcb_serial_number, 0) > 1 else 0
        else:
            form.duplicate_count = 0

    for form in service_forms:
        form.duplicate_count = service_serials.get(form.serial_number, 0) if service_serials.get(form.serial_number, 0) > 1 else 0
    
    context = {
        'user': user,
        'repairing_forms': repairing_forms,
        'inward_forms': inward_forms,
        'outward_forms': outward_forms,
        'service_forms': service_forms,
        'stock_requisitions': stock_requisitions,
        'dispatched_stock': dispatched_stock,
        # Repairing filters
        'repairing_date_from': repairing_date_from,
        'repairing_date_to': repairing_date_to,
        'repairing_search': repairing_search,
        # Inward filters
        'inward_date_from': inward_date_from,
        'inward_date_to': inward_date_to,
        'inward_search': inward_search,
        # Outward filters
        'outward_date_from': outward_date_from,
        'outward_date_to': outward_date_to,
        'outward_search': outward_search,
        # Service filters
        'service_date_from': service_date_from,
        'service_date_to': service_date_to,
        'service_search': service_search,
        # Stock requisition filters
        'stock_req_date_from': stock_req_date_from,
        'stock_req_date_to': stock_req_date_to,
        'stock_req_search': stock_req_search,
        'stock_req_status': stock_req_status,
        # Stock dispatched filters
        'stock_disp_date_from': stock_disp_date_from,
        'stock_disp_date_to': stock_disp_date_to,
        'stock_disp_search': stock_disp_search,
    }
    
    return render(request, 'forms/employee_data.html', context)


@login_required
def edit_employee_form(request, form_type, form_id):
    """Edit form submissions by employee"""
    user = request.user
    user_name = user.get_full_name() or user.username
    
    # Get the appropriate form based on type
    if form_type == 'repairing':
        form_obj = get_object_or_404(RepairingForm, id=form_id)
        form_class = RepairingFormForm
        redirect_url = 'forms:my_data'
    elif form_type == 'inward':
        form_obj = get_object_or_404(InwardForm, id=form_id)
        form_class = InwardFormForm
        redirect_url = 'forms:my_data'
    elif form_type == 'outward':
        form_obj = get_object_or_404(OutwardForm, id=form_id)
        form_class = OutwardFormForm
        redirect_url = 'forms:my_data'
    elif form_type == 'service':
        form_obj = get_object_or_404(ServiceReportForm, id=form_id)
        form_class = ServiceReportFormForm
        redirect_url = 'forms:my_data'
    else:
        return HttpResponseForbidden("Invalid form type")

    # Only allow editing if the logged-in user filled the form, or is a superuser
    if not (form_obj.user == user or user.is_superuser):
        return HttpResponseForbidden("You don't have permission to edit this form")
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=form_obj)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class(instance=form_obj)
    
    return render(request, 'forms/edit_employee_form.html', {
        'form': form,
        'form_type': form_type,
        'form_obj': form_obj,
    })


@login_required
def export_employee_data(request, form_type, format):
    """Export employee data to CSV or XLSX for a specific form type"""
    import io
    from datetime import datetime, timedelta
    
    user = request.user
    user_name = user.get_full_name() or user.username
    user_email = user.email
    
    # Get forms based on type with tab-specific filters (user's own entries only, but fields/headers match Team Data export)
    def get_user_display(obj):
        if hasattr(obj, 'user') and obj.user:
            return obj.user.get_full_name() or obj.user.username
        return '-'

    if form_type == 'repairing':
        date_from = request.GET.get('repairing_date_from', '')
        date_to = request.GET.get('repairing_date_to', '')
        search_query = request.GET.get('repairing_search', '')
        queryset = RepairingForm.objects.filter(
            Q(repaired_by__icontains=user_name) | Q(tested_by__icontains=user_name)
        )
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(case_number__icontains=search_query) |
                Q(customer_abbrev__icontains=search_query) |
                Q(inverter_id__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "repairing_forms"
        headers = [
            'Date', 'Case Number', 'Customer', 'Object', 'Inverter ID', 'PCB Serial Number', 'PCB Specification', 'PCB Rating',
            'Inverter Spec', 'Inverter Rating', 'Battery', 'Fault Location', 'Repair Content', 'Repaired By', 'Tested By', 'Filled By'
        ]
    elif form_type == 'inward':
        date_from = request.GET.get('inward_date_from', '')
        date_to = request.GET.get('inward_date_to', '')
        search_query = request.GET.get('inward_search', '')
        queryset = InwardForm.objects.filter(
            Q(email=user_email) | Q(received_by__icontains=user_name)
        )
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(customer_name__icontains=search_query) |
                Q(inverter_id__icontains=search_query) |
                Q(awb_lr_number__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "inward_forms"
        headers = [
            'Date', 'Inward Object', 'Customer Abbreviation', 'Customer Name', 'Inverter ID', 'Battery ID', 'PCB Serial Number',
            'Inverter Specification', 'Inverter Ratings', 'Battery Model', 'No of MPPT', 'Current/MPPT', 'PCB Quantity',
            'Received From Location', 'Received From District', 'Received From State', 'Pincode', 'Received By', 'Reason',
            'Transportation Mode', 'AWB Number', 'Filled By'
        ]
    elif form_type == 'outward':
        date_from = request.GET.get('outward_date_from', '')
        date_to = request.GET.get('outward_date_to', '')
        search_query = request.GET.get('outward_search', '')
        queryset = OutwardForm.objects.filter(
            Q(sent_by__icontains=user_name) | Q(approved_by__icontains=user_name)
        )
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(inverter_id_outward__icontains=search_query) |
                Q(sent_to_company__icontains=search_query) |
                Q(awb_number__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "outward_forms"
        headers = [
            'Date', 'Outward Object', 'Inverter ID (Outward)', 'Inverter Spec', 'Inverter Rating', 'Battery', 'Battery ID',
            'Sent To Company', 'Sent To Address', 'Sent To District', 'Sent To State', 'Pincode', 'Sent By', 'Approved By',
            'Control Card Changed', 'New Serial Number', 'Inverter ID (Inward)', 'Inverter Replaced', 'Delivered Through',
            'AWB Number', 'Remarks', 'Filled By'
        ]
    elif form_type == 'service':
        date_from = request.GET.get('service_date_from', '')
        date_to = request.GET.get('service_date_to', '')
        search_query = request.GET.get('service_search', '')
        queryset = ServiceReportForm.objects.filter(
            Q(email=user_email) | Q(engineer_first_name__icontains=user.first_name, engineer_last_name__icontains=user.last_name)
        )
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(serial_number__icontains=search_query) |
                Q(customer_first_name__icontains=search_query) |
                Q(customer_last_name__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "service_reports"
        headers = [
            'Engineer', 'Customer', 'Product Type', 'Serial Number', 'Service Date', 'Address', 'Battery Type', 'Battery Make',
            'Battery Voltage', 'PV Capacity (kW)', 'AC Cable Size', 'Physical Observation', 'Actual Work Done', 'Cause of Failure',
            'Conclusion', 'Customer Ratings', 'Suggestions', 'Created', 'Filled By'
        ]
    
    # Export based on format
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        writer = csv.writer(response)
        writer.writerow(headers)
        for obj in queryset:
            if form_type == 'repairing':
                writer.writerow([
                    obj.created_at.strftime('%d %b %Y'), obj.case_number, obj.customer_abbrev, obj.repairing_object, obj.inverter_id,
                    obj.pcb_serial_number, getattr(obj, 'pcb_specification', ''), getattr(obj, 'pcb_rating', ''), obj.inverter_spec, obj.inverter_rating, obj.battery,
                    obj.fault_location, obj.repair_content, obj.repaired_by, obj.tested_by, get_user_display(obj)
                ])
            elif form_type == 'inward':
                writer.writerow([
                    obj.created_at.strftime('%d %b %Y'), obj.inward_object, obj.customer_abbrev, obj.customer_name, obj.inverter_id, obj.battery_id,
                    obj.pcb_serial_number, obj.inverter_specs, obj.inverter_ratings, obj.battery, obj.no_of_mppt, obj.current_mppt, obj.pcb_quantity,
                    obj.received_from_location, obj.received_from_district, obj.received_from_state, obj.pincode, obj.received_by, obj.reason,
                    obj.transportation_mode, obj.awb_lr_number, get_user_display(obj)
                ])
            elif form_type == 'outward':
                writer.writerow([
                    obj.created_at.strftime('%d %b %Y'), obj.outward_object, obj.inverter_id_outward, obj.inverter_spec, obj.inverter_rating, obj.battery,
                    obj.battery_id, obj.sent_to_company, obj.sent_to_address, obj.sent_to_district, obj.sent_to_state, obj.pincode, obj.sent_by,
                    obj.approved_by, obj.control_card_changed, obj.new_serial_number, obj.inverter_id_inward, obj.inverter_replaced,
                    obj.delivered_through, obj.awb_number, obj.remarks, get_user_display(obj)
                ])
            elif form_type == 'service':
                writer.writerow([
                    f"{obj.engineer_first_name} {obj.engineer_last_name}", f"{obj.customer_first_name} {obj.customer_last_name}", obj.product_type,
                    obj.serial_number, obj.date_of_service.strftime('%d %b %Y') if obj.date_of_service else 'N/A',
                    f"{obj.address_street}, {obj.address_city}, {obj.address_state}, {obj.address_zip}", obj.battery_type, obj.battery_make,
                    obj.battery_voltage, obj.pv_capacity_kw, obj.ac_cable_size, obj.physical_observation, obj.actual_work_done,
                    obj.cause_of_failure, obj.conclusion, obj.customer_ratings, obj.suggestions, obj.created_at.strftime('%d %b %Y'), get_user_display(obj)
                ])
        return response
    elif format == 'xlsx':
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        wb = Workbook()
        ws = wb.active
        ws.title = filename_prefix.replace('_', ' ').title()
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        ws.append(headers)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
        for obj in queryset:
            if form_type == 'repairing':
                ws.append([
                    obj.created_at.strftime('%d %b %Y'), obj.case_number, obj.customer_abbrev, obj.repairing_object, obj.inverter_id,
                    obj.pcb_serial_number, getattr(obj, 'pcb_specification', ''), getattr(obj, 'pcb_rating', ''), obj.inverter_spec, obj.inverter_rating, obj.battery,
                    obj.fault_location, obj.repair_content, obj.repaired_by, obj.tested_by, get_user_display(obj)
                ])
            elif form_type == 'inward':
                ws.append([
                    obj.created_at.strftime('%d %b %Y'), obj.inward_object, obj.customer_abbrev, obj.customer_name, obj.inverter_id, obj.battery_id,
                    obj.pcb_serial_number, obj.inverter_specs, obj.inverter_ratings, obj.battery, obj.no_of_mppt, obj.current_mppt, obj.pcb_quantity,
                    obj.received_from_location, obj.received_from_district, obj.received_from_state, obj.pincode, obj.received_by, obj.reason,
                    obj.transportation_mode, obj.awb_lr_number, get_user_display(obj)
                ])
            elif form_type == 'outward':
                ws.append([
                    obj.created_at.strftime('%d %b %Y'), obj.outward_object, obj.inverter_id_outward, obj.inverter_spec, obj.inverter_rating, obj.battery,
                    obj.battery_id, obj.sent_to_company, obj.sent_to_address, obj.sent_to_district, obj.sent_to_state, obj.pincode, obj.sent_by,
                    obj.approved_by, obj.control_card_changed, obj.new_serial_number, obj.inverter_id_inward, obj.inverter_replaced,
                    obj.delivered_through, obj.awb_number, obj.remarks, get_user_display(obj)
                ])
            elif form_type == 'service':
                ws.append([
                    f"{obj.engineer_first_name} {obj.engineer_last_name}", f"{obj.customer_first_name} {obj.customer_last_name}", obj.product_type,
                    obj.serial_number, obj.date_of_service.strftime('%d %b %Y') if obj.date_of_service else 'N/A',
                    f"{obj.address_street}, {obj.address_city}, {obj.address_state}, {obj.address_zip}", obj.battery_type, obj.battery_make,
                    obj.battery_voltage, obj.pv_capacity_kw, obj.ac_cable_size, obj.physical_observation, obj.actual_work_done,
                    obj.cause_of_failure, obj.conclusion, obj.customer_ratings, obj.suggestions, obj.created_at.strftime('%d %b %Y'), get_user_display(obj)
                ])
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        return response
    else:
        return HttpResponse("Invalid format. Use 'csv' or 'xlsx'.", status=400)
    """Export employee data to CSV or XLSX"""
    import io
    from datetime import datetime
    
    user = request.user
    user_name = user.get_full_name() or user.username
    user_email = user.email
    
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Get all forms (same filtering logic as main view)
    repairing_forms = RepairingForm.objects.filter(
        Q(repaired_by__icontains=user_name) | 
        Q(tested_by__icontains=user_name)
    )
    inward_forms = InwardForm.objects.filter(
        Q(email=user_email) | 
        Q(received_by__icontains=user_name)
    )
    outward_forms = OutwardForm.objects.filter(
        Q(sent_by__icontains=user_name) | 
        Q(approved_by__icontains=user_name)
    )
    service_forms = ServiceReportForm.objects.filter(
        Q(email=user_email) |
        Q(engineer_first_name__icontains=user.first_name, engineer_last_name__icontains=user.last_name)
    )
    stock_requisitions = StockRequisition.objects.filter(
        manager_name__icontains=user_name
    )
    dispatched_stock = DispatchedStock.objects.filter(
        Q(dispatched_by__icontains=user_name) |
        Q(engineer_name__icontains=user_name)
    )
    
    # Apply filters
    if date_from:
        repairing_forms = repairing_forms.filter(created_at__gte=date_from)
        inward_forms = inward_forms.filter(created_at__gte=date_from)
        outward_forms = outward_forms.filter(created_at__gte=date_from)
        service_forms = service_forms.filter(created_at__gte=date_from)
        stock_requisitions = stock_requisitions.filter(created_at__gte=date_from)
        dispatched_stock = dispatched_stock.filter(created_at__gte=date_from)
    
    if date_to:
        repairing_forms = repairing_forms.filter(created_at__lte=date_to + ' 23:59:59')
        inward_forms = inward_forms.filter(created_at__lte=date_to + ' 23:59:59')
        outward_forms = outward_forms.filter(created_at__lte=date_to + ' 23:59:59')
        service_forms = service_forms.filter(created_at__lte=date_to + ' 23:59:59')
        stock_requisitions = stock_requisitions.filter(created_at__lte=date_to + ' 23:59:59')
        dispatched_stock = dispatched_stock.filter(created_at__lte=date_to + ' 23:59:59')
    
    if search_query:
        repairing_forms = repairing_forms.filter(
            Q(case_number__icontains=search_query) |
            Q(customer_abbrev__icontains=search_query) |
            Q(inverter_id__icontains=search_query)
        )
        inward_forms = inward_forms.filter(
            Q(customer_name__icontains=search_query) |
            Q(inverter_id__icontains=search_query) |
            Q(awb_lr_number__icontains=search_query)
        )
        outward_forms = outward_forms.filter(
            Q(inverter_id_outward__icontains=search_query) |
            Q(sent_to_company__icontains=search_query) |
            Q(awb_number__icontains=search_query)
        )
        service_forms = service_forms.filter(
            Q(serial_number__icontains=search_query) |
            Q(customer_first_name__icontains=search_query) |
            Q(customer_last_name__icontains=search_query)
        )
        stock_requisitions = stock_requisitions.filter(
            Q(serial_number__icontains=search_query) |
            Q(component_type__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        dispatched_stock = dispatched_stock.filter(
            Q(serial_number__icontains=search_query) |
            Q(component_type__icontains=search_query) |
            Q(tracking_number__icontains=search_query)
        )
    
    if status_filter:
        stock_requisitions = stock_requisitions.filter(status=status_filter)
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="my_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Repairing Forms
        writer.writerow(['=== REPAIRING FORMS ==='])
        writer.writerow(['Case Number', 'Customer', 'Object', 'Inverter ID', 'Repaired By', 'Tested By', 'Date', 'Status'])
        for form in repairing_forms:
            writer.writerow([
                form.case_number,
                form.customer_abbrev,
                form.repairing_object,
                form.inverter_id,
                form.repaired_by,
                form.tested_by,
                form.repaired_on_date,
                form.remark or 'Completed'
            ])
        writer.writerow([])
        
        # Inward Forms
        writer.writerow(['=== INWARD FORMS ==='])
        writer.writerow(['Customer', 'Inverter ID', 'From Location', 'Received By', 'Reason', 'AWB/LR', 'Date'])
        for form in inward_forms:
            writer.writerow([
                form.customer_name,
                form.inverter_id,
                f"{form.received_from_location}, {form.received_from_state}",
                form.received_by,
                form.reason,
                form.awb_lr_number,
                               form.created_at.strftime('%Y-%m-%d')
            ])
        writer.writerow([])
        
        # Outward Forms
        writer.writerow(['=== OUTWARD FORMS ==='])
        writer.writerow(['Inverter ID', 'Sent To', 'Location', 'Sent By', 'Approved By', 'AWB Number', 'Date'])
        for form in outward_forms:
            writer.writerow([
                form.inverter_id_outward,
                form.sent_to_company,
                f"{form.sent_to_district}, {form.sent_to_state}",
                form.sent_by,
                form.approved_by,
                form.awb_number,
                form.created_at.strftime('%Y-%m-%d')
            ])
        writer.writerow([])
        
        # Service Reports
        writer.writerow(['=== SERVICE REPORTS ==='])
        writer.writerow(['Engineer', 'Customer', 'Product Type', 'Serial Number', 'Service Date', 'Location', 'Created'])
        for form in service_forms:
            writer.writerow([
                f"{form.engineer_first_name} {form.engineer_last_name}",
                f"{form.customer_first_name} {form.customer_last_name}",
                form.product_type,
                form.serial_number,
                form.date_of_service.strftime('%Y-%m-%d') if form.date_of_service else 'N/A',
                f"{form.address_city}, {form.address_state}",
                form.created_at.strftime('%Y-%m-%d')
            ])
        writer.writerow([])
        
        # Stock Requisitions
        writer.writerow(['=== STOCK REQUISITIONS ==='])
        writer.writerow(['Serial Number', 'Component Type', 'Description', 'Qty Required', 'Qty Approved', 'Required To', 'Status', 'Created'])
        for req in stock_requisitions:
            writer.writerow([
                req.serial_number,
                req.component_type,
                req.description,
                req.quantity_required,
                req.approved_quantity or '—',
                req.required_to,
                req.get_status_display(),
                req.created_at.strftime('%Y-%m-%d')
            ])
        writer.writerow([])
        
        # Dispatched Stock
        writer.writerow(['=== STOCK DISPATCHED ==='])
        writer.writerow(['Serial Number', 'Component', 'Quantity', 'Engineer', 'Location', 'Courier', 'Tracking', 'Dispatch Date'])
        for stock in dispatched_stock:
            writer.writerow([
                stock.serial_number,
                stock.component_type,
                stock.quantity_dispatched,
                stock.engineer_name,
                stock.dispatch_location,
                stock.courier_name,
                stock.tracking_number,
                stock.dispatch_date.strftime('%Y-%m-%d')
            ])
        
        return response
    
    elif format == 'xlsx':
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            return HttpResponse("openpyxl library not installed. Please install it using: pip install openpyxl", status=500)
        
        wb = Workbook()
        ws = wb.active
        ws.title = filename_prefix.replace('_', ' ').title()
        
        # Set headers based on form type
        if form_type == 'repairing':
            headers = ['Case Number', 'Customer', 'Object', 'Inverter ID', 'Repaired By', 'Tested By', 'Date', 'Status']
            ws.append(headers)
            for cell in ws[1]:
                cell.font = Font(color="FFFFFF", bold=True)
                cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
            for form in queryset:
                ws.append([
                    form.case_number,
                    form.customer_abbrev,
                    form.repairing_object,
                    form.inverter_id,
                    form.repaired_by,
                    form.tested_by,
                    form.repaired_on_date,
                    form.remark or 'Completed'
                ])
        
        elif form_type == 'inward':
            headers = ['Customer', 'Inverter ID', 'From Location', 'Received By', 'Reason', 'AWB/LR', 'Date']
            ws.append(headers)
            for cell in ws[1]:
                cell.font = Font(color="FFFFFF", bold=True)
                cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
            for form in queryset:
                ws.append([
                    form.customer_name,
                    form.inverter_id,
                    f"{form.received_from_location}, {form.received_from_state}",
                    form.received_by,
                    form.reason,
                    form.awb_lr_number,
                    form.created_at.strftime('%Y-%m-%d')
                ])
        
        elif form_type == 'outward':
            headers = ['Inverter ID', 'Sent To', 'Location', 'Sent By', 'Approved By', 'AWB Number', 'Date']
            ws.append(headers)
            for cell in ws[1]:
                cell.font = Font(color="FFFFFF", bold=True)
                cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
            for form in queryset:
                ws.append([
                    form.inverter_id_outward,
                    form.sent_to_company,
                    f"{form.sent_to_district}, {form.sent_to_state}",
                    form.sent_by,
                    form.approved_by,
                    form.awb_number,
                    form.created_at.strftime('%Y-%m-%d')
                ])
        
        elif form_type == 'service':
            headers = ['Engineer', 'Customer', 'Product Type', 'Serial Number', 'Service Date', 'Location', 'Created']
            ws.append(headers)
            for cell in ws[1]:
                cell.font = Font(color="FFFFFF", bold=True)
                cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
            for form in queryset:
                ws.append([
                    f"{form.engineer_first_name} {form.engineer_last_name}",
                    f"{form.customer_first_name} {form.customer_last_name}",
                    form.product_type,
                    form.serial_number,
                    form.date_of_service.strftime('%Y-%m-%d') if form.date_of_service else 'N/A',
                    f"{form.address_city}, {form.address_state}",
                    form.created_at.strftime('%Y-%m-%d')
                ])
        
        elif form_type == 'stock-req':
            headers = ['Serial Number', 'Component Type', 'Description', 'Qty Required', 'Qty Approved', 'Required To', 'Status', 'Created']
            ws.append(headers)
            for cell in ws[1]:
                cell.font = Font(color="FFFFFF", bold=True)
                cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
            for req in queryset:
                ws.append([
                    req.serial_number,
                    req.component_type,
                    req.description,
                    req.quantity_required,
                    req.approved_quantity or '—',
                    req.required_to,
                    req.get_status_display(),
                    req.created_at.strftime('%Y-%m-%d')
                ])
        
        elif form_type == 'stock-disp':
            headers = ['Serial Number', 'Component', 'Quantity', 'Engineer', 'Location', 'Courier', 'Tracking', 'Dispatch Date']
            ws.append(headers)
            for cell in ws[1]:
                cell.font = Font(color="FFFFFF", bold=True)
                cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
            for stock in queryset:
                ws.append([
                    stock.serial_number,
                    stock.component_type,
                    stock.quantity_dispatched,
                    stock.engineer_name,
                    stock.dispatch_location,
                    stock.courier_name,
                    stock.tracking_number,
                    stock.dispatch_date.strftime('%Y-%m-%d')
                ])
        
        # Save to response
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        return response
    
    else:
        return HttpResponse("Invalid format. Use 'csv' or 'xlsx'.", status=400)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.contrib.auth.models import User
from .models import (RepairingForm, InwardForm, OutwardForm, 
                     ServiceReportForm, StockRequisition, DispatchedStock)
import csv


@login_required
def team_data_view(request):
    """Display all form responses from team members (for managers) or all data (for superusers)"""
    from datetime import datetime, timedelta
    from collections import Counter
    
    user = request.user
    
    # Check if user is superuser or manager
    if user.is_superuser:
        # Superuser sees all data
        team_users = User.objects.all()
        view_mode = 'all'
    elif hasattr(user, 'profile') and user.profile.get_team_members().exists():
        # Manager sees their team's data and their own data
        team_users = user.profile.get_team_members()
        if user not in team_users:
            team_users = team_users | User.objects.filter(pk=user.pk)
        view_mode = 'team'
    else:
        # Regular user - redirect to personal data view
        from django.contrib import messages
        messages.warning(request, "You don't have permission to view team data. Showing your personal data instead.")
        return redirect('forms:my_data')
    
    # Get team members names and emails
    team_names = [u.get_full_name() or u.username for u in team_users]
    team_emails = list(team_users.values_list('email', flat=True))
    
    # Get tab-specific filter parameters
    repairing_date_from = request.GET.get('repairing_date_from', '')
    repairing_date_to = request.GET.get('repairing_date_to', '')
    repairing_search = request.GET.get('repairing_search', '')
    
    inward_date_from = request.GET.get('inward_date_from', '')
    inward_date_to = request.GET.get('inward_date_to', '')
    inward_search = request.GET.get('inward_search', '')
    
    outward_date_from = request.GET.get('outward_date_from', '')
    outward_date_to = request.GET.get('outward_date_to', '')
    outward_search = request.GET.get('outward_search', '')
    
    service_date_from = request.GET.get('service_date_from', '')
    service_date_to = request.GET.get('service_date_to', '')
    service_search = request.GET.get('service_search', '')
    
    stock_req_date_from = request.GET.get('stock_req_date_from', '')
    stock_req_date_to = request.GET.get('stock_req_date_to', '')
    stock_req_search = request.GET.get('stock_req_search', '')
    stock_req_status = request.GET.get('stock_req_status', '')
    
    stock_disp_date_from = request.GET.get('stock_disp_date_from', '')
    stock_disp_date_to = request.GET.get('stock_disp_date_to', '')
    stock_disp_search = request.GET.get('stock_disp_search', '')
    
    # Build queries for team data
    # For superusers, get all records. For managers, filter by team members
    if view_mode == 'all':
        # Superuser - get all records
        repairing_forms = RepairingForm.objects.all()
    else:
        # Manager - filter by team members (user who filled the form or name match)
        repairing_q = Q(user__in=team_users)
        for name in team_names:
            repairing_q |= Q(repaired_by__icontains=name) | Q(tested_by__icontains=name)
        repairing_forms = RepairingForm.objects.filter(repairing_q)
    if repairing_date_from:
        from_date = datetime.strptime(repairing_date_from, '%Y-%m-%d')
        repairing_forms = repairing_forms.filter(created_at__gte=from_date)
    if repairing_date_to:
        to_date = datetime.strptime(repairing_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        repairing_forms = repairing_forms.filter(created_at__lt=end_date)
    if repairing_search:
        repairing_forms = repairing_forms.filter(
            Q(case_number__icontains=repairing_search) |
            Q(customer_abbrev__icontains=repairing_search) |
            Q(inverter_id__icontains=repairing_search)
        )
    repairing_forms = repairing_forms.order_by('-created_at')
    
    # Inward Forms
    if user.is_superuser:
        inward_forms = InwardForm.objects.all()
    elif view_mode == 'all':
        inward_forms = InwardForm.objects.all()
    else:
        inward_q = Q(user__in=team_users)
        for email in team_emails:
            inward_q |= Q(email=email)
        for name in team_names:
            inward_q |= Q(received_by__icontains=name)
        inward_forms = InwardForm.objects.filter(inward_q)
    if inward_date_from:
        from_date = datetime.strptime(inward_date_from, '%Y-%m-%d')
        inward_forms = inward_forms.filter(created_at__gte=from_date)
    if inward_date_to:
        to_date = datetime.strptime(inward_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        inward_forms = inward_forms.filter(created_at__lt=end_date)
    if inward_search:
        inward_forms = inward_forms.filter(
            Q(customer_name__icontains=inward_search) |
            Q(inverter_id__icontains=inward_search) |
            Q(awb_lr_number__icontains=inward_search)
        )
    inward_forms = inward_forms.order_by('-created_at')
    
    # Outward Forms
    if view_mode == 'all':
        outward_forms = OutwardForm.objects.all()
    else:
        outward_q = Q(user__in=team_users)
        for name in team_names:
            outward_q |= Q(sent_by__icontains=name) | Q(approved_by__icontains=name)
        outward_forms = OutwardForm.objects.filter(outward_q)
    if outward_date_from:
        from_date = datetime.strptime(outward_date_from, '%Y-%m-%d')
        outward_forms = outward_forms.filter(created_at__gte=from_date)
    if outward_date_to:
        to_date = datetime.strptime(outward_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        outward_forms = outward_forms.filter(created_at__lt=end_date)
    if outward_search:
        outward_forms = outward_forms.filter(
            Q(inverter_id_outward__icontains=outward_search) |
            Q(sent_to_company__icontains=outward_search) |
            Q(awb_number__icontains=outward_search)
        )
    outward_forms = outward_forms.order_by('-created_at')
    
    # Service Report Forms
    if view_mode == 'all':
        service_forms = ServiceReportForm.objects.all()
    else:
        service_q = Q(user__in=team_users)
        for email in team_emails:
            service_q |= Q(email=email)
        for user_obj in team_users:
            service_q |= Q(engineer_first_name__icontains=user_obj.first_name, engineer_last_name__icontains=user_obj.last_name)
        service_forms = ServiceReportForm.objects.filter(service_q)
    if service_date_from:
        from_date = datetime.strptime(service_date_from, '%Y-%m-%d')
        service_forms = service_forms.filter(created_at__gte=from_date)
    if service_date_to:
        to_date = datetime.strptime(service_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        service_forms = service_forms.filter(created_at__lt=end_date)
    if service_search:
        service_forms = service_forms.filter(
            Q(serial_number__icontains=service_search) |
            Q(customer_first_name__icontains=service_search) |
            Q(customer_last_name__icontains=service_search)
        )
    service_forms = service_forms.order_by('-created_at')
    
    # Stock Requisitions
    if view_mode == 'all':
        stock_requisitions = StockRequisition.objects.all()
    else:
        stock_req_q = Q(user__in=team_users)
        for name in team_names:
            stock_req_q |= Q(manager_name__icontains=name)
        stock_requisitions = StockRequisition.objects.filter(stock_req_q)
    if stock_req_date_from:
        from_date = datetime.strptime(stock_req_date_from, '%Y-%m-%d')
        stock_requisitions = stock_requisitions.filter(created_at__gte=from_date)
    if stock_req_date_to:
        to_date = datetime.strptime(stock_req_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        stock_requisitions = stock_requisitions.filter(created_at__lt=end_date)
    if stock_req_search:
        stock_requisitions = stock_requisitions.filter(
            Q(serial_number__icontains=stock_req_search) |
            Q(component_type__icontains=stock_req_search) |
            Q(description__icontains=stock_req_search)
        )
    if stock_req_status:
        stock_requisitions = stock_requisitions.filter(status=stock_req_status)
    stock_requisitions = stock_requisitions.order_by('-created_at')
    
    # Dispatched Stock
    if view_mode == 'all':
        dispatched_stock = DispatchedStock.objects.all()
    else:
        dispatched_q = Q(user__in=team_users)
        for name in team_names:
            dispatched_q |= Q(dispatched_by__icontains=name) | Q(engineer_name__icontains=name)
        dispatched_stock = DispatchedStock.objects.filter(dispatched_q)
    if stock_disp_date_from:
        from_date = datetime.strptime(stock_disp_date_from, '%Y-%m-%d')
        dispatched_stock = dispatched_stock.filter(created_at__gte=from_date)
    if stock_disp_date_to:
        to_date = datetime.strptime(stock_disp_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        dispatched_stock = dispatched_stock.filter(created_at__lt=end_date)
    if stock_disp_search:
        dispatched_stock = dispatched_stock.filter(
            Q(serial_number__icontains=stock_disp_search) |
            Q(component_type__icontains=stock_disp_search) |
            Q(tracking_number__icontains=stock_disp_search)
        )
    dispatched_stock = dispatched_stock.order_by('-created_at')
    
    # Calculate duplicate serial numbers PER FORM TYPE (not across all forms)
    from collections import Counter
    
    # Count duplicates separately for each form type (excluding stock forms)
    repairing_serials = Counter(repairing_forms.values_list('inverter_id', flat=True))
    inward_serials = Counter(inward_forms.values_list('inverter_id', flat=True))
    outward_serials = Counter(outward_forms.values_list('inverter_id_outward', flat=True))
    service_serials = Counter(service_forms.values_list('serial_number', flat=True))
    
    # Annotate each object with duplicate count (only within its own form type)
    for form in repairing_forms:
        form.duplicate_count = repairing_serials.get(form.inverter_id, 0) if repairing_serials.get(form.inverter_id, 0) > 1 else 0
    
    for form in inward_forms:
        form.duplicate_count = inward_serials.get(form.inverter_id, 0) if inward_serials.get(form.inverter_id, 0) > 1 else 0
    
    for form in outward_forms:
        form.duplicate_count = outward_serials.get(form.inverter_id_outward, 0) if outward_serials.get(form.inverter_id_outward, 0) > 1 else 0
    
    for form in service_forms:
        form.duplicate_count = service_serials.get(form.serial_number, 0) if service_serials.get(form.serial_number, 0) > 1 else 0
    
    # Stock Inverters: InwardForm entries whose inverter_id is NOT in OutwardForm, filtered by team
    outward_ids = set(OutwardForm.objects.values_list('inverter_id_outward', flat=True))
    if view_mode == 'all':
        stock_inverters_qs = InwardForm.objects.exclude(inverter_id__in=outward_ids)
    else:
        stock_inverters_qs = InwardForm.objects.exclude(inverter_id__in=outward_ids).filter(user__in=team_users)
    # Apply Stock Inverters tab filters (date/search)
    stock_inv_date_from = request.GET.get('stock_inv_date_from', '')
    stock_inv_date_to = request.GET.get('stock_inv_date_to', '')
    stock_inv_search = request.GET.get('stock_inv_search', '')
    if stock_inv_date_from:
        from_date = datetime.strptime(stock_inv_date_from, '%Y-%m-%d')
        stock_inverters_qs = stock_inverters_qs.filter(created_at__gte=from_date)
    if stock_inv_date_to:
        to_date = datetime.strptime(stock_inv_date_to, '%Y-%m-%d')
        end_date = to_date + timedelta(days=1)
        stock_inverters_qs = stock_inverters_qs.filter(created_at__lt=end_date)
    if stock_inv_search:
        stock_inverters_qs = stock_inverters_qs.filter(
            Q(inverter_id__icontains=stock_inv_search) |
            Q(customer_name__icontains=stock_inv_search) |
            Q(received_from_location__icontains=stock_inv_search) |
            Q(received_from_state__icontains=stock_inv_search) |
            Q(received_by__icontains=stock_inv_search) |
            Q(reason__icontains=stock_inv_search) |
            Q(awb_lr_number__icontains=stock_inv_search)
        )
    stock_inverters = stock_inverters_qs.order_by('-created_at')

    # Add 'Filled By' and 'Date Filled' columns for stock inverters
    stock_inverters_display = []
    for form in stock_inverters:
        stock_inverters_display.append({
            'form': form,
            'filled_by': form.user.get_full_name() if form.user else '',
            'date_filled': form.created_at.strftime('%Y-%m-%d'),
        })

    # Build unified all_entries list for 'All Entries' tab
    all_entries = []
    for form in repairing_forms:
        all_entries.append({
            'form_type': 'Repairing',
            'serial': getattr(form, 'inverter_id', ''),
            'customer': getattr(form, 'customer_abbrev', ''),
            'date': form.created_at.strftime('%Y-%m-%d'),
            'remark': getattr(form, 'remark', getattr(form, 'status', '')),
        })
    for form in inward_forms:
        all_entries.append({
            'form_type': 'Inward',
            'serial': getattr(form, 'inverter_id', ''),
            'customer': getattr(form, 'customer_name', ''),
            'date': form.created_at.strftime('%Y-%m-%d'),
            'remark': getattr(form, 'remark', '')
        })
    for form in outward_forms:
        all_entries.append({
            'form_type': 'Outward',
            'serial': getattr(form, 'inverter_id_outward', ''),
            'customer': getattr(form, 'sent_to_company', ''),
            'date': form.created_at.strftime('%Y-%m-%d'),
            'remark': getattr(form, 'remark', '')
        })
    for form in service_forms:
        all_entries.append({
            'form_type': 'Service',
            'serial': getattr(form, 'serial_number', ''),
            'customer': f"{getattr(form, 'customer_first_name', '')} {getattr(form, 'customer_last_name', '')}",
            'date': form.created_at.strftime('%Y-%m-%d'),
            'remark': getattr(form, 'actual_work_done', getattr(form, 'suggestions', ''))
        })
    for form in stock_requisitions:
        all_entries.append({
            'form_type': 'Stock Requisition',
            'serial': getattr(form, 'serial_number', ''),
            'customer': getattr(form, 'component_type', ''),
            'date': form.created_at.strftime('%Y-%m-%d'),
            'remark': getattr(form, 'description', '')
        })
    for form in dispatched_stock:
        all_entries.append({
            'form_type': 'Dispatched Stock',
            'serial': getattr(form, 'serial_number', ''),
            'customer': getattr(form, 'engineer_name', ''),
            'date': form.created_at.strftime('%Y-%m-%d'),
            'remark': getattr(form, 'dispatch_remarks', '')
        })
    context = {
        'user': user,
        'view_mode': view_mode,
        'team_users': team_users,
        'repairing_forms': repairing_forms,
        'inward_forms': inward_forms,
        'outward_forms': outward_forms,
        'service_forms': service_forms,
        'stock_requisitions': stock_requisitions,
        'dispatched_stock': dispatched_stock,
        'stock_inverters': stock_inverters,
        'stock_inverters_display': stock_inverters_display,
        'stock_inv_date_from': stock_inv_date_from,
        'stock_inv_date_to': stock_inv_date_to,
        'stock_inv_search': stock_inv_search,
        # Repairing filters
        'repairing_date_from': repairing_date_from,
        'repairing_date_to': repairing_date_to,
        'repairing_search': repairing_search,
        # Inward filters
        'inward_date_from': inward_date_from,
        'inward_date_to': inward_date_to,
        'inward_search': inward_search,
        # Outward filters
        'outward_date_from': outward_date_from,
        'outward_date_to': outward_date_to,
        'outward_search': outward_search,
        # Service filters
        'service_date_from': service_date_from,
        'service_date_to': service_date_to,
        'service_search': service_search,
        # Stock requisition filters
        'stock_req_date_from': stock_req_date_from,
        'stock_req_date_to': stock_req_date_to,
        'stock_req_search': stock_req_search,
        'stock_req_status': stock_req_status,
        # Stock dispatched filters
        'stock_disp_date_from': stock_disp_date_from,
        'stock_disp_date_to': stock_disp_date_to,
        'stock_disp_search': stock_disp_search,
        'all_entries': all_entries,
    }
    
    return render(request, 'forms/team_data.html', context)


@login_required
def export_team_data(request, form_type, format):
    """Export team data to CSV or XLSX for managers/superusers"""
    import io
    from datetime import datetime, timedelta
    
    user = request.user
    
    # Check permissions
    if user.is_superuser:
        team_users = User.objects.all()
        view_mode = 'all'
    elif hasattr(user, 'profile') and user.profile.team_members.exists():
        team_users = user.profile.get_team_members()
        view_mode = 'team'
    else:
        return HttpResponseForbidden("You don't have permission to export team data")
    
    team_names = [u.get_full_name() or u.username for u in team_users]
    team_emails = list(team_users.values_list('email', flat=True))
    
    # Get forms based on type with tab-specific filters
    if form_type == 'repairing':
        date_from = request.GET.get('repairing_date_from', '')
        date_to = request.GET.get('repairing_date_to', '')
        search_query = request.GET.get('repairing_search', '')
        
        if view_mode == 'all':
            queryset = RepairingForm.objects.all()
        else:
            repairing_q = Q()
            for name in team_names:
                repairing_q |= Q(repaired_by__icontains=name) | Q(tested_by__icontains=name)
            queryset = RepairingForm.objects.filter(repairing_q)
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(case_number__icontains=search_query) |
                Q(customer_abbrev__icontains=search_query) |
                Q(inverter_id__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "team_repairing_forms"
        headers = [
            'Date', 'Case Number', 'Customer', 'Object', 'Inverter ID', 'PCB Serial Number', 'PCB Specification', 'PCB Rating',
            'Inverter Spec', 'Inverter Rating', 'Battery', 'Fault Location', 'Repair Content', 'Repaired By', 'Tested By', 'Filled By'
        ]
        
    elif form_type == 'inward':
        date_from = request.GET.get('inward_date_from', '')
        date_to = request.GET.get('inward_date_to', '')
        search_query = request.GET.get('inward_search', '')
        
        if view_mode == 'all':
            queryset = InwardForm.objects.all()
        else:
            inward_q = Q()
            for email in team_emails:
                inward_q |= Q(email=email)
            for name in team_names:
                inward_q |= Q(received_by__icontains=name)
            queryset = InwardForm.objects.filter(inward_q)
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(customer_name__icontains=search_query) |
                Q(inverter_id__icontains=search_query) |
                Q(awb_lr_number__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "team_inward_forms"
        headers = [
            'Date', 'Inward Object', 'Customer Abbreviation', 'Customer Name', 'Inverter ID', 'Battery ID', 'PCB Serial Number',
            'Inverter Specification', 'Inverter Ratings', 'Battery Model', 'No of MPPT', 'Current/MPPT', 'PCB Quantity',
            'Received From Location', 'Received From District', 'Received From State', 'Pincode', 'Received By', 'Reason',
            'Transportation Mode', 'AWB Number', 'Filled By'
        ]
        
    elif form_type == 'outward':
        date_from = request.GET.get('outward_date_from', '')
        date_to = request.GET.get('outward_date_to', '')
        search_query = request.GET.get('outward_search', '')
        
        if view_mode == 'all':
            queryset = OutwardForm.objects.all()
        else:
            outward_q = Q()
            for name in team_names:
                outward_q |= Q(sent_by__icontains=name) | Q(approved_by__icontains=name)
            queryset = OutwardForm.objects.filter(outward_q)
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(inverter_id_outward__icontains=search_query) |
                Q(sent_to_company__icontains=search_query) |
                Q(awb_number__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "team_outward_forms"
        headers = [
            'Date', 'Outward Object', 'Inverter ID (Outward)', 'Inverter Spec', 'Inverter Rating', 'Battery', 'Battery ID',
            'Sent To Company', 'Sent To Address', 'Sent To District', 'Sent To State', 'Pincode', 'Sent By', 'Approved By',
            'Control Card Changed', 'New Serial Number', 'Inverter ID (Inward)', 'Inverter Replaced', 'Delivered Through',
            'AWB Number', 'Remarks', 'Filled By'
        ]
        
    elif form_type == 'service':
        date_from = request.GET.get('service_date_from', '')
        date_to = request.GET.get('service_date_to', '')
        search_query = request.GET.get('service_search', '')
        
        if view_mode == 'all':
            queryset = ServiceReportForm.objects.all()
        else:
            service_q = Q()
            for email in team_emails:
                service_q |= Q(email=email)
            for user_obj in team_users:
                service_q |= Q(engineer_first_name__icontains=user_obj.first_name, engineer_last_name__icontains=user_obj.last_name)
            queryset = ServiceReportForm.objects.filter(service_q)
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(serial_number__icontains=search_query) |
                Q(customer_first_name__icontains=search_query) |
                Q(customer_last_name__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "team_service_reports"
        headers = [
            'Engineer', 'Customer', 'Product Type', 'Serial Number', 'Service Date', 'Address', 'Battery Type', 'Battery Make',
            'Battery Voltage', 'PV Capacity (kW)', 'AC Cable Size', 'Physical Observation', 'Actual Work Done', 'Cause of Failure',
            'Conclusion', 'Customer Ratings', 'Suggestions', 'Created', 'Filled By'
        ]
        
    elif form_type == 'stock-req':
        date_from = request.GET.get('stock_req_date_from', '')
        date_to = request.GET.get('stock_req_date_to', '')
        search_query = request.GET.get('stock_req_search', '')
        status_filter = request.GET.get('stock_req_status', '')
        
        if view_mode == 'all':
            queryset = StockRequisition.objects.all()
        else:
            stock_req_q = Q()
            for name in team_names:
                stock_req_q |= Q(manager_name__icontains=name)
            queryset = StockRequisition.objects.filter(stock_req_q)
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(serial_number__icontains=search_query) |
                Q(component_type__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        queryset = queryset.order_by('-created_at')
        filename_prefix = "team_stock_requisitions"
        headers = ['Serial Number', 'Component', 'Quantity', 'Manager', 'Status', 'Date']
        
    elif form_type == 'stock-disp':
        date_from = request.GET.get('stock_disp_date_from', '')
        date_to = request.GET.get('stock_disp_date_to', '')
        search_query = request.GET.get('stock_disp_search', '')
        
        if view_mode == 'all':
            queryset = DispatchedStock.objects.all()
        else:
            dispatched_q = Q()
            for name in team_names:
                dispatched_q |= Q(dispatched_by__icontains=name) | Q(engineer_name__icontains=name)
            queryset = DispatchedStock.objects.filter(dispatched_q)
        if date_from:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=from_date)
        if date_to:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        if search_query:
            queryset = queryset.filter(
                Q(serial_number__icontains=search_query) |
                Q(component_type__icontains=search_query) |
                Q(tracking_number__icontains=search_query)
            )
        queryset = queryset.order_by('-created_at')
        filename_prefix = "team_dispatched_stock"
        headers = ['Serial Number', 'Component', 'Quantity', 'Engineer', 'Courier', 'Tracking', 'Date']
    
    else:
        return HttpResponse("Invalid form type", status=400)
    
    # Export based on format
    def get_user_display(obj):
        if hasattr(obj, 'user') and obj.user:
            return obj.user.get_full_name() or obj.user.username
        return '-'

    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(headers)
        
        for obj in queryset:
            if form_type == 'repairing':
                writer.writerow([
                    obj.created_at.strftime('%d %b %Y'), obj.case_number, obj.customer_abbrev, obj.repairing_object, obj.inverter_id,
                    obj.pcb_serial_number, obj.pcb_specification, obj.pcb_rating, obj.inverter_spec, obj.inverter_rating, obj.battery,
                    obj.fault_location, obj.repair_content, obj.repaired_by, obj.tested_by, get_user_display(obj)
                ])
            elif form_type == 'inward':
                writer.writerow([
                    obj.created_at.strftime('%d %b %Y'), obj.inward_object, obj.customer_abbrev, obj.customer_name, obj.inverter_id, obj.battery_id,
                    obj.pcb_serial_number, obj.inverter_specs, obj.inverter_ratings, obj.battery, obj.no_of_mppt, obj.current_mppt, obj.pcb_quantity,
                    obj.received_from_location, obj.received_from_district, obj.received_from_state, obj.pincode, obj.received_by, obj.reason,
                    obj.transportation_mode, obj.awb_lr_number, get_user_display(obj)
                ])
            elif form_type == 'outward':
                writer.writerow([
                    obj.created_at.strftime('%d %b %Y'), obj.outward_object, obj.inverter_id_outward, obj.inverter_spec, obj.inverter_rating, obj.battery,
                    obj.battery_id, obj.sent_to_company, obj.sent_to_address, obj.sent_to_district, obj.sent_to_state, obj.pincode, obj.sent_by,
                    obj.approved_by, obj.control_card_changed, obj.new_serial_number, obj.inverter_id_inward, obj.inverter_replaced,
                    obj.delivered_through, obj.awb_number, obj.remarks, get_user_display(obj)
                ])
            elif form_type == 'service':
                writer.writerow([
                    f"{obj.engineer_first_name} {obj.engineer_last_name}", f"{obj.customer_first_name} {obj.customer_last_name}", obj.product_type,
                    obj.serial_number, obj.date_of_service.strftime('%d %b %Y') if obj.date_of_service else 'N/A',
                    f"{obj.address_street}, {obj.address_city}, {obj.address_state}, {obj.address_zip}", obj.battery_type, obj.battery_make,
                    obj.battery_voltage, obj.pv_capacity_kw, obj.ac_cable_size, obj.physical_observation, obj.actual_work_done,
                    obj.cause_of_failure, obj.conclusion, obj.customer_ratings, obj.suggestions, obj.created_at.strftime('%d %b %Y'), get_user_display(obj)
                ])
            elif form_type == 'stock-req':
                writer.writerow([obj.serial_number, obj.component_type, obj.quantity_required, obj.manager_name, obj.status, obj.created_at.strftime('%Y-%m-%d')])
            elif form_type == 'stock-disp':
                writer.writerow([obj.serial_number, obj.component_type, obj.quantity_dispatched, obj.engineer_name, obj.courier_name, obj.tracking_number, obj.dispatch_date.strftime('%Y-%m-%d')])
        
        return response

    elif format == 'xlsx':
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        
        wb = Workbook()
        ws = wb.active
        ws.title = form_type.replace('-', ' ').title()
        
        # Header styling
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        ws.append(headers)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
        
        for obj in queryset:
            if form_type == 'repairing':
                ws.append([
                    obj.created_at.strftime('%d %b %Y'), obj.case_number, obj.customer_abbrev, obj.repairing_object, obj.inverter_id,
                    obj.pcb_serial_number, obj.pcb_specification, obj.pcb_rating, obj.inverter_spec, obj.inverter_rating, obj.battery,
                    obj.fault_location, obj.repair_content, obj.repaired_by, obj.tested_by, get_user_display(obj)
                ])
            elif form_type == 'inward':
                ws.append([
                    obj.created_at.strftime('%d %b %Y'), obj.inward_object, obj.customer_abbrev, obj.customer_name, obj.inverter_id, obj.battery_id,
                    obj.pcb_serial_number, obj.inverter_specs, obj.inverter_ratings, obj.battery, obj.no_of_mppt, obj.current_mppt, obj.pcb_quantity,
                    obj.received_from_location, obj.received_from_district, obj.received_from_state, obj.pincode, obj.received_by, obj.reason,
                    obj.transportation_mode, obj.awb_lr_number, get_user_display(obj)
                ])
            elif form_type == 'outward':
                ws.append([
                    obj.created_at.strftime('%d %b %Y'), obj.outward_object, obj.inverter_id_outward, obj.inverter_spec, obj.inverter_rating, obj.battery,
                    obj.battery_id, obj.sent_to_company, obj.sent_to_address, obj.sent_to_district, obj.sent_to_state, obj.pincode, obj.sent_by,
                    obj.approved_by, obj.control_card_changed, obj.new_serial_number, obj.inverter_id_inward, obj.inverter_replaced,
                    obj.delivered_through, obj.awb_number, obj.remarks, get_user_display(obj)
                ])
            elif form_type == 'service':
                ws.append([
                    f"{obj.engineer_first_name} {obj.engineer_last_name}", f"{obj.customer_first_name} {obj.customer_last_name}", obj.product_type,
                    obj.serial_number, obj.date_of_service.strftime('%d %b %Y') if obj.date_of_service else 'N/A',
                    f"{obj.address_street}, {obj.address_city}, {obj.address_state}, {obj.address_zip}", obj.battery_type, obj.battery_make,
                    obj.battery_voltage, obj.pv_capacity_kw, obj.ac_cable_size, obj.physical_observation, obj.actual_work_done,
                    obj.cause_of_failure, obj.conclusion, obj.customer_ratings, obj.suggestions, obj.created_at.strftime('%d %b %Y'), get_user_display(obj)
                ])
            elif form_type == 'stock-req':
                ws.append([obj.serial_number, obj.component_type, obj.quantity_required, obj.manager_name, obj.status, obj.created_at.strftime('%Y-%m-%d')])
            elif form_type == 'stock-disp':
                ws.append([obj.serial_number, obj.component_type, obj.quantity_dispatched, obj.engineer_name, obj.courier_name, obj.tracking_number, obj.dispatch_date.strftime('%Y-%m-%d')])
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        return response

    else:
        return HttpResponse("Invalid format. Use 'csv' or 'xlsx'.", status=400)
# Import login_required decorator
from django.contrib.auth.decorators import login_required
