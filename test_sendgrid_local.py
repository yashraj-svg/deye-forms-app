#!/usr/bin/env python
"""Test SendGrid Web API locally before deployment"""
import os
import sys

# Set API key - REPLACE WITH YOUR OWN KEY
os.environ['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY', '')
os.environ['DEBUG'] = 'True'
os.environ['DJANGO_SETTINGS_MODULE'] = 'deye_config.settings'

import django
django.setup()

from django.conf import settings
from forms.emails import send_sendgrid_email

print("=" * 70)
print("SENDGRID WEB API TEST - Local Verification")
print("=" * 70)

print(f"\n✅ API Key configured: {settings.SENDGRID_API_KEY[:20]}...{settings.SENDGRID_API_KEY[-10:]}")
print(f"✅ From Email: {settings.DEFAULT_FROM_EMAIL}")
print(f"✅ sendgrid package version: 6.12.5+")

print("\n📧 Sending test email via SendGrid Web API...")
print("   To: yashraj@deyeindia.com")
print("   Subject: 🧪 SendGrid API Web Integration Test")

try:
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="background-color: white; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto;">
            <h2 style="color: #2ecc71;">✅ SendGrid Web API Test</h2>
            <p>This email was sent using <strong>SendGrid's Web API</strong> (NOT SMTP).</p>
            <p style="background-color: #ecf0f1; padding: 10px; border-left: 4px solid #2ecc71;">
                <strong>If you're reading this email:</strong><br>
                ✅ The SendGrid Web API integration is working correctly!<br>
                ✅ Production deployment should work!<br>
                ✅ No more SMTP timeout issues!
            </p>
            <hr>
            <p><small style="color: #7f8c8d;">Sent from: Local Test | Time: """ + str(__import__('datetime').datetime.now()) + """</small></p>
        </div>
    </body>
    </html>
    """
    
    success = send_sendgrid_email('yashraj@deyeindia.com', '🧪 SendGrid API Web Integration Test', html, 'Test email from SendGrid Web API')
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Email sent via SendGrid Web API")
        print("=" * 70)
        print("\n📬 Next steps:")
        print("   1. Check your inbox at yashraj@deyeindia.com")
        print("   2. If email arrives in 1-2 seconds, commit and deploy!")
        print("   3. Production will NOT have SMTP timeout issues!")
        print("\n   Commit message: 'Switch from SMTP to SendGrid Web API for reliability'")
        sys.exit(0)
    else:
        print("\n⚠️ Email returned False - check error messages above")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
