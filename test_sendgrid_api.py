#!/usr/bin/env python
"""
Test SendGrid Web API email sending locally
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.emails import send_sendgrid_email
from django.conf import settings

print("=" * 60)
print("Testing SendGrid Web API Email Sending")
print("=" * 60)

# Check API key
api_key = settings.SENDGRID_API_KEY
if not api_key:
    print("❌ ERROR: SENDGRID_API_KEY not set in environment!")
    print("Set it with: $env:SENDGRID_API_KEY='your-key-here'")
    exit(1)

print(f"✅ API Key configured: {api_key[:10]}...{api_key[-10:]}")
print(f"✅ From Email: {settings.DEFAULT_FROM_EMAIL}")

# Test email parameters
to_email = "yashraj@deyeindia.com"
subject = "🧪 Test Email from SendGrid Web API"
html_content = """
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>✅ SendGrid Web API Test Email</h2>
    <p>This is a <strong>test email</strong> sent via SendGrid's <strong>Web API</strong> (not SMTP).</p>
    <p><strong>Sent at:</strong> """ + str(__import__('datetime').datetime.now()) + """</p>
    <p><strong>From:</strong> """ + settings.DEFAULT_FROM_EMAIL + """</p>
    <p><strong>To:</strong> """ + to_email + """</p>
    <hr>
    <p><small>If you're reading this, the SendGrid Web API integration is working! 🎉</small></p>
</body>
</html>
"""
plain_content = "Test email from SendGrid Web API"

# Send test email
print("\n📧 Sending test email...")
print(f"   To: {to_email}")
print(f"   Subject: {subject}")

try:
    success = send_sendgrid_email(to_email, subject, html_content, plain_content)
    
    if success:
        print("\n✅ SUCCESS! Email sent via SendGrid Web API")
        print("   Check your inbox at yashraj@deyeindia.com")
        print("\n   If email arrives, the production deployment will work!")
    else:
        print("\n⚠️ WARNING: Email sending returned False")
        print("   Check the error messages above")
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
