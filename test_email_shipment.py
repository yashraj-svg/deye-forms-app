#!/usr/bin/env python
"""
Test email sending for shipment notifications
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape

# Test data
items = [
    {'serial_number': '20110103100263', 'component_type': 'MCU', 'description': '16-bit processor', 'quantity_received': 20},
    {'serial_number': '20110103100169', 'component_type': 'PCB', 'description': 'Green PCB 10x10', 'quantity_received': 20},
    {'serial_number': 'UNKNOWN_SN', 'component_type': '', 'description': '', 'quantity_received': 100},
]
total_qty = sum(item['quantity_received'] for item in items)
shipment_date = '2026-02-05'

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

# Send test email
try:
    subject = f"📦 New Shipment Received - {len(items)} Items ({int(total_qty)} units)"
    from_email = os.environ.get('DEFAULT_FROM_EMAIL', 'yashraj@deyeindia.com')
    recipient_list = ['snehal@deyeindia.com', 'nilesh@deyeindia.com', 'yashraj@deyeindia.com']
    
    msg = EmailMultiAlternatives(subject, 'New shipment received', from_email, recipient_list)
    msg.attach_alternative(email_html, "text/html")
    
    # Try to send (will use console backend in local dev if EMAIL_BACKEND not configured)
    result = msg.send(fail_silently=True)
    
    print(f"✅ Email test successful!")
    print(f"Subject: {subject}")
    print(f"From: {from_email}")
    print(f"To: {', '.join(recipient_list)}")
    print(f"Items: {len(items)}")
    print(f"Total Qty: {int(total_qty)}")
    print(f"Shipment Date: {shipment_date}")
    
except Exception as e:
    print(f"❌ Email test failed: {str(e)}")
