from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import StockItem


def send_requisition_email(requisition):
    """Send email notification for a single requisition (legacy, kept for compatibility)."""
    
    # Get current stock for the serial number
    stock_item = StockItem.objects.filter(pcba_sn_new=requisition.serial_number).order_by('-year').first()
    current_quantity = stock_item.quantity if stock_item else 0
    remaining_after_approval = current_quantity - requisition.quantity_required if current_quantity else 0
    
    # Email context
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    context = {
        'requisition': requisition,
        'current_quantity': current_quantity,
        'remaining_after_approval': remaining_after_approval,
        'approval_url': f"{site_url}/admin/forms/stockrequisition/{requisition.id}/change/",
    }
    
    # Render email template
    html_message = render_to_string('forms/emails/requisition_approval.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email
    send_mail(
        subject=f'Stock Requisition for {requisition.serial_number} - {requisition.component_type}',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['snehal@deyeindia.com', 'nilesh@deyeindia.com'],
        html_message=html_message,
        fail_silently=False,
    )


def send_bulk_requisition_email(requisitions, engineer_name, required_to):
    """Send consolidated email for multiple requisitions in one submission."""
    
    try:
        site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        
        # Prepare items with stock information
        items_with_stock = []
        total_requested_qty = 0
        for req in requisitions:
            stock_item = StockItem.objects.filter(pcba_sn_new=req.serial_number).order_by('-year').first()
            current_quantity = stock_item.quantity if stock_item else 0
            remaining_after_requested = current_quantity - req.quantity_required
            
            items_with_stock.append({
                'requisition': req,
                'current_quantity': current_quantity,
                'remaining_after_requested': remaining_after_requested,
                'approval_url': f"{site_url}/admin/forms/stockrequisition/{req.id}/change/",
            })
            total_requested_qty += req.quantity_required
        
        # Email context
        context = {
            'items': items_with_stock,
            'engineer_name': engineer_name,
            'required_to': required_to,
            'total_items': len(requisitions),
            'total_requested_qty': total_requested_qty,
            'submission_date': requisitions[0].created_at if requisitions else None,
        }
        
        # Render email template
        try:
            html_message = render_to_string('forms/emails/bulk_requisition_approval.html', context)
            plain_message = strip_tags(html_message)
        except Exception as template_error:
            print(f"Template rendering error: {str(template_error)}")
            # Fallback to plain text email
            plain_message = f"""
Stock Requisition Batch - {engineer_name}

{len(requisitions)} items requested for: {required_to}
Total Quantity Requested: {total_requested_qty}

Please login to the admin panel to review and approve these requisitions.
            """
            html_message = None
        
        # Send email with fail_silently=True to prevent crashes
        from django.core.mail import EmailMultiAlternatives
        subject = f'Stock Requisition Batch - {engineer_name} - {len(requisitions)} Component(s)'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['snehal@deyeindia.com', 'nilesh@deyeindia.com', 'yashraj@deyeindia.com']
        
        msg = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
        if html_message:
            msg.attach_alternative(html_message, "text/html")
        
        msg.send(fail_silently=True)
        print(f"✅ Email sent for {len(requisitions)} requisitions")
        
    except Exception as e:
        print(f"❌ Error in send_bulk_requisition_email: {str(e)}")
        import traceback
        traceback.print_exc()
        # Don't raise - let the process continue
