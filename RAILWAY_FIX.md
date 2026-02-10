# 🚂 RAILWAY DEPLOYMENT FIX

Your Railway PostgreSQL database has old duplicate data. Here's how to fix it.

## 📊 Problem Analysis

Your current Railway database shows:
- **Total Items**: 1,069
- **Total Quantity**: 6,480,600 PCS ❌ (Should be 259,406)
- **Issue**: Old data with tripled values, or loaded multiple times

## ✅ Solution: Clean & Reload Database

### Option 1: Using Provided Script (RECOMMENDED)

Push the cleanup script to GitHub first:

```bash
# On your local machine
git add railway_cleanup.py
git commit -m "add: Railway database cleanup script"
git push origin master
```

Then on Railway, run:

```bash
# SSH to Railway or use Railway CLI
cd /app
python railway_cleanup.py
```

This will:
1. ✅ Delete all 1,069 old items (with inflated quantities)
2. ✅ Load 1,976 correct items from fixture
3. ✅ Show before/after comparison
4. ✅ Verify exact quantities (259,406 PCS)

---

### Option 2: Manual Railway Commands

SSH into your Railway container:

```bash
# Connect to Railway shell
railway run bash
# Or: railway shell

# Navigate to app
cd /app

# Run Django commands
python manage.py shell << EOF
from forms.models import StockItem
print(f"Items before: {StockItem.objects.count()}")
# Delete all
StockItem.objects.all().delete()
print(f"Items after delete: {StockItem.objects.count()}")
EOF

# Load fixture
python manage.py loaddata stock_items

# Or reload from Excel
python manage.py load_akshay_stock --clear

# Verify
python manage.py shell << EOF
from forms.models import StockItem
from django.db.models import Sum
count = StockItem.objects.count()
qty = StockItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
print(f"Final: {count} items, {qty:.0f} PCS")
EOF
```

---

### Option 3: Using Railway Dashboard

1. Go to Railway Dashboard
2. Open your PostgreSQL database
3. Use built-in query tool to run:

```sql
TRUNCATE forms_stockitem CASCADE;
```

Then in your app's shell:

```bash
python manage.py loaddata stock_items
```

---

## 🔧 Why PostgreSQL vs SQLite?

Your local machine uses **SQLite** (file-based):
- File: `db.sqlite3`
- Fixed data: 1,976 items, 259,406 PCS

Railway uses **PostgreSQL** (client-server):
- Hosted on Railway servers
- Had old data before deployment
- Needs to be cleaned and reloaded

---

## 📋 QUICKEST FIX (Copy & Paste)

### Step 1: Push cleanup script
```bash
git add railway_cleanup.py
git commit -m "add: Railway cleanup script"
git push origin master
```

### Step 2: SSH to Railway (or use Railway CLI)
```bash
# Option A: Railway CLI
railway shell
cd /app

# Option B: Direct SSH
ssh -t app@railway...
```

### Step 3: Run cleanup
```bash
python railway_cleanup.py
```

### Step 4: Restart and verify
```bash
# Restart Railway app through dashboard OR:
railway run restart

# Then check: https://deycindia.in/stock/received/
# Should show: 1,085 items, 259,406 PCS
```

---

## 🐘 PostgreSQL Specific Notes

Railway uses PostgreSQL with these details:
- Connection: Secure connection string in environment variables
- Database: Automatically managed by Railway
- Backups: Railway handles daily backups
- You can't delete database, only truncate tables

### To reset PostgreSQL (most thorough):

```bash
# Option 1: Truncate the table (recommended)
python manage.py dbshell << EOF
TRUNCATE TABLE forms_stockitem CASCADE;
EOF

# Then reload
python manage.py loaddata stock_items
```

---

## ✨ Expected Results After Fix

### Before Cleanup:
```
Total Items: 1,069
Total Quantity: 6,480,600 PCS ❌
```

### After Cleanup & Reload:
```
Total Items: 1,085 (merged/deduplicated)
Total Quantity: 259,406 PCS ✅
```

### For 2025 only:
```
Year: 2025
Total Items: 552
Total Quantity: 92,448 PCS
```

---

## 🆘 If Cleanup Fails

### Error: "Cannot connect to database"
→ Check DATABASE_URL environment variable in Railway
→ Make sure PostgreSQL service is running

### Error: "Fixture not found"
→ Run: `python manage.py loaddata forms/fixtures/stock_items.json`
→ Or: `python manage.py load_akshay_stock --clear`

### Error: "Still showing old data"
→ Restart Railway app through dashboard
→ Clear browser cache (Ctrl+Shift+Delete)
→ Wait 30 seconds for cold start

### Data still large after reload
→ Check if fixture file is correct: `forms/fixtures/stock_items.json`
→ Or use Excel loader: `python manage.py load_akshay_stock --clear`

---

## 🔐 Railway Environment Variables

Make sure these are set in Railway:

```
DATABASE_URL=postgresql://...  [Railway auto-sets this]
DJANGO_SETTINGS_MODULE=deye_config.settings
DEBUG=False
```

Check them:
```bash
railway status  # Shows environment
```

---

## 📝 Summary

| Step | Action | Command |
|------|--------|---------|
| 1 | Add cleanup script | `git push origin master` |
| 2 | Connect to Railway | `railway shell` |
| 3 | Run cleanup | `python railway_cleanup.py` |
| 4 | Restart app | Railway dashboard |
| 5 | Verify | Visit website, check quantities |

---

## 🎯 Expected After Fix

```
deycindia.in/stock/received/

Total Items: 1,085
Total Quantity: 259,406 PCS ✅

No errors ✅
Correct quantities ✅
All items visible ✅
```

---

## 📞 Quick Reference

| Issue | Solution |
|-------|----------|
| Quantities too large | Run `railway_cleanup.py` |
| PostgreSQL connection failed | Check DATABASE_URL in Railway |
| Data not changing | Restart app + clear browser cache |
| Fixture not loading | Check file path and permissions |

Just run the cleanup script and you'll be fixed! 🚀
