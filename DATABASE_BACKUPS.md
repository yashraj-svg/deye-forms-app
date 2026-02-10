# Automated Database Backups to S3

## Overview

Your Deye Web App now has a complete backup system with:
- **Stock Data Backups**: Daily JSON snapshots of all 1,976 StockItem records
- **Full Database Backups**: Complete database backups (SQLite locally, PostgreSQL on Railway)

Both run automatically on a schedule and upload to AWS S3.

## Quick Start

### 1. Verify AWS Credentials Locally

```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_REGION=ap-south-1
export S3_BUCKET_NAME=deyeindia-backups

# Test stock backup
python manage.py backup_to_s3

# Test database backup
python manage.py backup_full_database --to-s3
```

### 2. Deploy to Railway

1. Go to [Railway Dashboard](https://railway.app/project/b66f07cc-cbc5-41fe-8a6a-2707f8a0196f)
2. Click **Deye Logs** → **Variables**
3. Add these environment variables:
   ```
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   AWS_REGION=ap-south-1
   S3_BUCKET_NAME=deyeindia-backups
   ENABLE_BACKUPS=true
   ```
4. Save and redeploy

### 3. Monitor Backups

```bash
# Check logs
railway logs | grep -i backup

# You should see at scheduled times:
# 📦 Running scheduled stock backup...
# ✅ Stock backup completed successfully
# 💾 Running scheduled database backup...
# ✅ Database backup completed successfully
```

## Backup Schedule

| Type | Time | Frequency | Keeps | Size |
|------|------|-----------|-------|------|
| **Stock Data** | 02:00 UTC | Daily | Last 30 | ~900 KB |
| **Full Database** | 03:00 UTC | Daily | Last 10 | ~3-5 MB |

## Backup Management Commands

### backup_to_s3
Stock data backup (all StockItem records)

```bash
# Just create local backup
python manage.py backup_to_s3

# Create AND upload to S3
python manage.py backup_to_s3
# (automatically uploads when AWS credentials are set)
```

**Features:**
- Exports 1,976 items as JSON
- ~900 KB compressed
- Keeps last 30 backups
- AES256 encryption

### backup_full_database
Full database backup

```bash
# Create local backup only
python manage.py backup_full_database

# Create AND upload to S3
python manage.py backup_full_database --to-s3

# Use custom S3 bucket
python manage.py backup_full_database --to-s3 --bucket=my-bucket
```

**Features:**
- SQLite: Copies database file (3.55 MB)
- PostgreSQL: Creates SQL dump
- Keeps last 10 backups
- AES256 encryption

## AWS Setup Details

### S3 Bucket: deyeindia-backups

```bash
# List all backups
aws s3 ls s3://deyeindia-backups/ --recursive

# View backup details
aws s3 ls s3://deyeindia-backups/database-backups/
aws s3 ls s3://deyeindia-backups/daily-backups/
```

### IAM User: deye-backup-bot

**Permissions:**
- s3:PutObject - Upload backups
- s3:DeleteObject - Clean up old backups
- s3:ListBucket - List contents

**Restricts to:** `deyeindia-backups` bucket only

## Restore Procedures

### Restore Stock Data

```bash
# 1. Download backup
aws s3 cp s3://deyeindia-backups/daily-backups/stock_backup_2026-02-10.json .

# 2. Load into database
python manage.py loaddata stock_backup_2026-02-10.json
```

### Restore Full Database (SQLite)

```bash
# 1. Download backup
aws s3 cp s3://deyeindia-backups/database-backups/db_backup_sqlite_2026-02-10.db .

# 2. Replace database
cp db_backup_sqlite_2026-02-10.db db.sqlite3

# 3. Restart Django
python manage.py runserver
```

### Restore Full Database (PostgreSQL)

```bash
# 1. Download backup
aws s3 cp s3://deyeindia-backups/database-backups/db_backup_postgres_2026-02-10.sql .

# 2. Get PostgreSQL connection
railway status

# 3. Restore
psql -h <host> -U <user> -d <database> < db_backup_postgres_2026-02-10.sql
```

## Storage Costs

**S3 Pricing**: $0.025/GB/month (ap-south-1)

**Your Usage:**
- Stock backups: 30 × 0.9 MB = 27 MB
- Database backups: 10 × 4 MB = 40 MB
- **Total: ~70 MB = < $0.02/month**

## Troubleshooting

### Backup not running on Railway?

```bash
# 1. Check ENABLE_BACKUPS is set
railway variables

# 2. Check logs for errors
railway logs | tail -30

# 3. Verify AWS credentials are correct
# Re-run test locally before deploying
```

### AccessDenied error from S3?

```
Error: "User deye-backup-bot is not authorized to perform: s3:PutObject"
```

**Solution:**
1. Go to [IAM → Users → deye-backup-bot](https://console.aws.amazon.com/iam/home#/users/deye-backup-bot)
2. Click **Add inline policy**
3. Create policy with S3 permissions (paste JSON from S3_BACKUP_SETUP.md)

### "This command only works with PostgreSQL"?

```bash
# Old error message - now fixed!
# backup_full_database now supports both SQLite and PostgreSQL
# If you see this error, update to latest version:
git pull origin master
```

### Backup file not in S3?

```bash
# 1. Did you run with --to-s3 flag?
python manage.py backup_full_database --to-s3

# 2. Are AWS credentials set?
env | grep AWS

# 3. Check S3 bucket exists
aws s3 ls | grep deyeindia-backups

# 4. Check IAM permissions
aws s3 ls s3://deyeindia-backups/
```

## File Locations

### S3 Bucket Structure

```
deyeindia-backups/
├── daily-backups/
│   └── stock_backup_2026-02-10-14-00-00.json      (stock data)
└── database-backups/
    ├── db_backup_sqlite_2026-02-10-14-00-00.db     (SQLite - local)
    └── db_backup_postgres_2026-02-10-14-00-00.sql  (PostgreSQL - Railway)
```

### Local Code Files

```
forms/
├── backup_scheduler.py                              (scheduler setup)
└── management/commands/
    ├── backup_to_s3.py                              (stock data backup)
    └── backup_full_database.py                      (full database backup)
```

## Security

✅ **Encryption**: All S3 objects use AES256 server-side encryption
✅ **IAM Policy**: Backup user restricted to S3 only
✅ **Access Keys**: Stored as Railway environment variables  
✅ **Retention**: Old backups auto-deleted after limit reached
✅ **Versioning**: S3 keeps version history

## Monitoring

### Check S3 Usage
```bash
aws s3 ls s3://deyeindia-backups/ --recursive --human-readable --summarize
```

### View Backup Metadata
```bash
# See backup timestamp, encryption, size, checksum
aws s3api head-object \
  --bucket deyeindia-backups \
  --key database-backups/db_backup_sqlite_2026-02-10.db
```

### Get Backup Stats
```bash
# How many of each backup type exists?
aws s3 ls s3://deyeindia-backups/database-backups/ | wc -l
aws s3 ls s3://deyeindia-backups/daily-backups/ | wc -l
```

## Next Steps

- [x] Create S3 bucket
- [x] Create IAM user
- [x] Test locally
- [ ] Deploy to Railway
- [ ] Set ENABLE_BACKUPS=true
- [ ] Verify first backup run (check logs)
- [ ] Test restore procedure

## Support

If backups aren't working:
1. Check Railway logs: `railway logs | grep -i backup`
2. Verify AWS credentials are set: `railway variables`
3. Test locally: `python manage.py backup_full_database --to-s3`
4. Check S3 bucket access: `aws s3 ls s3://deyeindia-backups/`

---

**Last Updated:** 2026-02-10  
**Backup System:** Unified SQLite + PostgreSQL support  
**Status:** ✅ Ready for production
