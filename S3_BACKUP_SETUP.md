# S3 Backup Setup Guide

## 1. Get Your AWS Credentials

### Option A: Create IAM User for Backups (Recommended)
1. Go to: https://console.aws.amazon.com/iam/home
2. Click **Users** → **Create user**
3. Name: `deye-backup-bot`
4. Skip permissions (we'll add inline policy)
5. Click **Create user**
6. Go to **Permissions** → **Add inline policy**
7. Use this policy (replace `YOUR-BUCKET-NAME`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::YOUR-BUCKET-NAME/*",
                "arn:aws:s3:::YOUR-BUCKET-NAME"
            ]
        }
    ]
}
```

8. Go to **Security credentials** → **Create access key**
9. Choose "Application running outside AWS"
10. Copy your **Access Key ID** and **Secret Access Key**

### Option B: Use Root AWS Credentials
(Less secure, but faster for testing)
1. Go to: https://console.aws.amazon.com/
2. Click your name → **Security Credentials**
3. Expand **Access Keys**
4. Create new access key (if you don't have one)
5. Copy the credentials

---

## 2. Create S3 Bucket

### Create a bucket for backups:
```bash
aws s3 mb s3://deye-db-backups --region us-east-1
```

Or via AWS Console:
1. Go to: https://s3.console.aws.amazon.com/s3/home
2. Click **Create bucket**
3. Name: `deye-db-backups`
4. Region: `us-east-1` (or your preferred region)
5. Click **Create**

---

## 3. Add Environment Variables

### For Local Testing:
Create `.env` file in project root:

```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=deye-db-backups
ENABLE_BACKUPS=true
```

Then load in your terminal:
```bash
# Windows PowerShell
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
$env:AWS_REGION="us-east-1"
$env:S3_BUCKET_NAME="deye-db-backups"
$env:ENABLE_BACKUPS="true"

# Or using python-dotenv locally
pip install python-dotenv
```

### For Railway (Production):
1. Go to Railway Dashboard: https://railway.com
2. Open your project → **web** service
3. Click **Variables**
4. Add these variables:
   - `AWS_ACCESS_KEY_ID` = your access key
   - `AWS_SECRET_ACCESS_KEY` = your secret key
   - `AWS_REGION` = us-east-1
   - `S3_BUCKET_NAME` = deye-db-backups
   - `ENABLE_BACKUPS` = true

---

## 4. Test Locally

### Install packages:
```bash
pip install -r requirements.txt
```

### Run manual backup:
```bash
python manage.py backup_to_s3
```

Expected output:
```
📦 Creating backup: stock_backup_2026-02-10-14-30-45.json
   Found 1976 items, 259406.00 PCS
   Uploading to S3...
✅ Backup uploaded successfully!
   S3 Location: s3://deye-db-backups/daily-backups/stock_backup_2026-02-10-14-30-45.json

🧹 Cleaning up old backups (keeping last 30)...
   ✓ All 1 backups are recent

✅ BACKUP COMPLETE!
```

### View backups in S3:
```bash
aws s3 ls s3://deye-db-backups/daily-backups/ --human-readable
```

Or via AWS Console:
1. Go to S3 → Your bucket → `daily-backups/` folder
2. You should see your backup files

---

## 5. Deploy to Railway

### Push code changes:
```bash
git add requirements.txt forms/apps.py forms/backup_scheduler.py forms/management/commands/backup_to_s3.py
git commit -m "Add S3 automated backup functionality

- Daily JSON backups of StockItem data
- Automatic cleanup keeping last 30 backups
- Uses APScheduler for reliable scheduling"
git push origin master
```

### Railway will auto-deploy

### Check logs:
```bash
railway logs --tail 50
```

You should see:
```
✅ Backup scheduler started - Daily backups at 02:00 UTC
```

---

## 6. Restore From Backup

### Download backup from S3:
```bash
aws s3 cp s3://deye-db-backups/daily-backups/stock_backup_2026-02-10-14-30-45.json .
```

### Load into database:
```bash
# Extract the data portion
python manage.py shell
>>> import json
>>> with open('stock_backup_2026-02-10-14-30-45.json') as f:
...     backup = json.load(f)
...     data = backup['data']  # Extract just the data array
...     with open('restore_data.json', 'w') as out:
...         json.dump(data, out)
>>> exit()

# Load the fixture
python manage.py loaddata restore_data.json
```

---

## 7. Troubleshooting

### "AWS credentials not found"
- Verify environment variables are set
- Check spelling: `AWS_ACCESS_KEY_ID` (not `AWS_KEY`)
- Make sure you're using the correct key format

### "Access Denied" error
- Check IAM policy in AWS console
- Verify bucket name matches in policy
- Ensure S3_BUCKET_NAME environment variable is correct

### Scheduler not running
- Check `ENABLE_BACKUPS=true` is set
- Check logs: `railway logs | grep -i backup`
- Ensure APScheduler installed: `pip install apscheduler>=3.10.0`

### Backup takes too long
- Normal for large datasets (1976 items = ~873KB)
- S3 upload usually takes <5 seconds
- Check railway logs for performance details

---

## 💡 Tips

1. **Daily backups at 2 AM UTC** - Adjust in `backup_scheduler.py` line 26
2. **Keeps last 30 backups** - Adjust cleanup in `backup_to_s3.py` line 96
3. **Manual backup anytime:**
   ```bash
   python manage.py backup_to_s3
   ```
4. **Check backup size in S3:**
   ```bash
   aws s3 ls s3://deye-db-backups/daily-backups/ --summarize --human-readable
   ```

---

**Backup is now automated and secure!** 🔐
