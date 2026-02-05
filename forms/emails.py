from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import StockItem
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


def send_sendgrid_email(to_emails, subject, html_content, plain_content=None):
    """
    Send email using SendGrid Web API (not SMTP).
    
    Args:
        to_emails: list of email addresses or single email
        subject: email subject
        html_content: HTML email body
        plain_content: plain text fallback (optional)
    """
    if isinstance(to_emails, str):
        to_emails = [to_emails]
    
    try:
        if not settings.SENDGRID_API_KEY:
            print(f"[EMAIL] ⚠️ SENDGRID_API_KEY not set, skipping email to {to_emails}")
            return False
        
        print(f"[EMAIL] Preparing SendGrid email to: {to_emails}")
        
        # Create Mail object
        mail = Mail(
            from_email=Email(settings.DEFAULT_FROM_EMAIL),
            to_emails=[To(email) for email in to_emails],
            subject=subject,
            plain_text_content=plain_content or strip_tags(html_content),
            html_content=html_content
        )
        
        # Send via SendGrid API
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        print(f"[EMAIL] Sending email via SendGrid API...")
        response = sg.send(mail)
        
        print(f"[EMAIL] ✅ SendGrid API response: {response.status_code}")
        return response.status_code in [200, 201, 202]
        
    except Exception as e:
        print(f"[EMAIL] ❌ SendGrid API error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_requisition_email(requisition):
    """Send email notification for a single requisition using SendGrid API."""
    
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
    
    # Send email via SendGrid API
    subject = f'Stock Requisition for {requisition.serial_number} - {requisition.component_type}'
    send_sendgrid_email(['snehal@deyeindia.com', 'nilesh@deyeindia.com'], subject, html_message, plain_message)


def send_bulk_requisition_email(requisitions, engineer_name, required_to):
    """Send consolidated email for multiple requisitions using SendGrid API."""
    
    # Run email sending in a thread to avoid blocking the request
    import threading
    import time
    
    def _send_email():
        try:
            time.sleep(0.1)  # Give thread a moment to start
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
                print(f"[EMAIL] Template rendering error: {str(template_error)}")
                # Fallback to plain text email
                plain_message = f"""Stock Requisition Batch - {engineer_name}

{len(requisitions)} items requested for: {required_to}
Total Quantity Requested: {total_requested_qty}

Please login to the admin panel to review and approve these requisitions."""
                html_message = f"<p>{plain_message.replace(chr(10), '<br>')}</p>"
            
            # Send email via SendGrid API
            subject = f'Stock Requisition Batch - {engineer_name} - {len(requisitions)} Component(s)'
            recipient_list = ['yashraj@deyeindia.com']
            
            print(f"[EMAIL] 📧 Preparing stock requisition email for {len(requisitions)} items")
            success = send_sendgrid_email(recipient_list, subject, html_message, plain_message)
            
            if success:
                print(f"[EMAIL] ✅ Email thread completed successfully for {len(requisitions)} requisitions")
            else:
                print(f"[EMAIL] ⚠️ Email thread completed with warnings/errors")
            
        except Exception as e:
            print(f"[EMAIL] ❌ Error in _send_email: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Start email sending in background thread (non-blocking)
    email_thread = threading.Thread(target=_send_email, daemon=False)
    email_thread.start()
    print(f"[EMAIL] 🧵 Background thread started for {len(requisitions)} requisitions")
