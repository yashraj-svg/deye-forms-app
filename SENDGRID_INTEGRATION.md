# SendGrid Email Integration for Shipment Updates

## Overview
Automatic email notifications are sent to the stock team when new shipments are added through the "Update New Shipments" feature.

## Email Recipients
- `snehal@deyeindia.com` (Snehal Shine - Stock Manager)
- `nilesh@deyeindia.com` (Nilesh - Stock Team)
- `yashraj@deyeindia.com` (Yashraj - Developer/Admin)

## Email Content

### Subject Line
```
📦 New Shipment Received - {COUNT} Items ({TOTAL_QTY} units)
```

Example:
```
📦 New Shipment Received - 3 Items (140 units)
```

### Email Body
The email includes:

1. **Header** - Professional green gradient with "📦 New Shipment Received"
2. **Shipment Date** - When the shipment was received
3. **Items Table** - Shows:
   - Serial Number
   - Component Type
   - Description
   - Quantity for each item
4. **Total Summary** - Shows total quantity in a highlighted box
5. **Footer** - Link to www.deyeindia.in

## How It Works

### When Email is Sent
- User fills in shipment items (via bulk paste or manual entry)
- User clicks "Update Shipments" button
- User reviews and confirms on confirmation page
- **Email is sent automatically** when confirmed

### Email Features
✅ **HTML formatted** - Professional look with colors and styling  
✅ **Auto-escapes** - Prevents HTML injection for security  
✅ **Fail-safe** - Email errors don't crash the application  
✅ **Error logging** - Failures are logged to console  
✅ **Async-friendly** - Ready for background job queue (future)

## Configuration

### Local Testing (Development)
By default, Django uses console email backend in development:
- Emails are printed to console/logs
- Useful for testing without sending real emails
- Set `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` in settings.py

### Production (Railway)
Uses SendGrid SMTP:
- `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'`
- `EMAIL_HOST = 'smtp.sendgrid.net'`
- `EMAIL_PORT = 587`
- `EMAIL_HOST_USER = 'apikey'`
- `EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')`

### Environment Variables Needed
On Railway, set:
```
DEFAULT_FROM_EMAIL = yashraj@deyeindia.com
SENDGRID_API_KEY = SG.Acf-HQcBBy_F6efY2lhvg.S8D3N8Q48FgJUmeEgwQVrSy-8boX0kC611FSSIw
```

## Testing Locally

### Test 1: Verify Email Logic
```bash
python test_email_shipment.py
```
Expected output:
```
✅ Email test successful!
Subject: 📦 New Shipment Received - 3 Items (140 units)
From: yashraj@deyeindia.com
To: snehal@deyeindia.com, nilesh@deyeindia.com, yashraj@deyeindia.com
Items: 3
Total Qty: 140
```

### Test 2: Through Web Interface
1. Go to http://127.0.0.1:8000/stock/update-new-shipments/
2. Add items (manually or bulk paste)
3. Click "Update Shipments"
4. Review and confirm
5. **Email should be sent** (check Django console/logs)
6. Look for print output in terminal showing email was sent

### Test 3: With Actual SendGrid
1. Get SendGrid API key from account
2. Set environment variable: `SENDGRID_API_KEY=your_key`
3. Set `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'`
4. Test sending email - check SendGrid dashboard

## Email Design

### Color Scheme
- **Primary Green**: `#059669` - Header and highlights
- **Light Green**: `#ecfdf5` - Total quantity box
- **Neutral Gray**: `#f1f5f9`, `#475569` - Text and dividers

### Responsiveness
- ✅ Mobile-friendly design
- ✅ Works in all email clients (Gmail, Outlook, Apple Mail, etc.)
- ✅ Fallback fonts if custom fonts not available

## Error Handling

### What Happens If Email Fails
1. Application continues normally ✅
2. Error logged to console (for debugging)
3. User sees success message on screen (email still saved)
4. Shipment data is saved to database regardless

### Why This Approach
- Email is not critical for core functionality
- Stock data is safely stored in database
- Temporary email issues don't block operations

## Future Enhancements

1. **Attachment** - Add CSV with item details
2. **Recurring Summary** - Daily digest of all shipments
3. **SMS Alerts** - Critical shipments via SMS (needs Twilio)
4. **Database Log** - Store all sent emails in database
5. **Resend Option** - Admin can resend email from UI
6. **Template Engine** - Use Django templates for emails
7. **Background Queue** - Use Celery for async sending

## Debugging

### Check Email Backend
```python
from django.conf import settings
print(settings.EMAIL_BACKEND)
```

### Manual Test
```python
from django.core.mail import send_mail
send_mail(
    'Test Subject',
    'Test Message',
    'yashraj@deyeindia.com',
    ['snehal@deyeindia.com'],
    fail_silently=False,
)
```

### Check SendGrid Status
- Dashboard: app.sendgrid.com
- Check Activity Feed for sent emails
- Verify API key is active

## Support

If emails are not being sent:
1. ✅ Check SENDGRID_API_KEY is set on Railway
2. ✅ Verify recipient email addresses are correct
3. ✅ Check Django logs for errors
4. ✅ Test with local console backend first
5. ✅ Verify SendGrid account is active (not trial expired)
