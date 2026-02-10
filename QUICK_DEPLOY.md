# 🚀 QUICK DEPLOYMENT COMMANDS FOR deycindia.in

Copy and paste these commands on your web server to deploy the latest updates.

---

## ⚡ FASTEST WAY (Python Script - 1 Command)

### SSH into your server and run:

```bash
cd /home/deycindia/app  # Update with your actual path
python deploy.py
```

**Done!** The script will automatically:
- ✅ Pull latest code from GitHub
- ✅ Install dependencies
- ✅ Run migrations (auto-loads 1,976 stock items)
- ✅ Collect static files
- ✅ Verify data
- ✅ Show completion status

---

## 🐧 FOR LINUX SERVERS

```bash
# 1. SSH into server
ssh user@deycindia.in

# 2. Navigate to project
cd /home/deycindia/app  # Update path

# 3. Make script executable
chmod +x deploy.sh

# 4. Edit script (update PROJECT_DIR path)
nano deploy.sh
# Find line: PROJECT_DIR="/path/to/deye-forms-app"
# Change to: PROJECT_DIR="/home/deycindia/app"
# Save: Ctrl+X, Y, Enter

# 5. Run deployment
./deploy.sh
```

---

## 🪟 FOR WINDOWS SERVER / IIS

```powershell
# 1. Open PowerShell as Administrator

# 2. Navigate to project
cd C:\inetpub\deye-app  # Update your actual path

# 3. Pull latest code
git pull origin master

# 4. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run migrations
python manage.py migrate

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Restart IIS app pool
Restart-WebAppPool -Name "DeyeApp"  # Use your app pool name
```

---

## 🔄 MANUAL DEPLOYMENT (Step by Step)

If scripts don't work, use these commands:

```bash
# SSH into server
ssh user@deycindia.in

# Navigate to project directory
cd /path/to/deye-forms-app

# STEP 1: Pull latest code from GitHub
git fetch origin
git pull origin master

# STEP 2: Activate virtual environment
source .venv/bin/activate
# For Windows: .venv\Scripts\Activate.ps1

# STEP 3: Install dependencies
pip install -r requirements.txt

# STEP 4: Run migrations (auto-loads stock data)
python manage.py migrate

# STEP 5: Collect static files
python manage.py collectstatic --noinput

# STEP 6: Restart web server
sudo systemctl restart deye-app
# OR for other servers:
# sudo service gunicorn restart
# sudo systemctl restart nginx
# Restart-WebAppPool -Name "DeyeApp"  (Windows)

# STEP 7: Verify deployment
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()
from forms.models import StockItem
from django.db.models import Sum
count = StockItem.objects.count()
qty = StockItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
print(f'Stock Items: {count} (expected: 1976)')
print(f'Total Quantity: {qty:.0f} PCS (expected: 259406)')
"
```

---

## ✅ VERIFICATION CHECKLIST

After deployment, check these:

- [ ] No errors during `git pull`
- [ ] No errors during `python manage.py migrate`
- [ ] No errors during `collectstatic`
- [ ] Web server restarted successfully
- [ ] Can access: `https://deycindia.in/stock/received/`
- [ ] Page shows **1,085 total items**
- [ ] Page shows **259,406 PCS** quantity
- [ ] No TypeError or sorting errors
- [ ] Can view stock items with serial numbers
- [ ] Can view items with blank serial numbers

---

## 📊 EXPECT TO SEE

### Before Deployment:
```
Total Items: 552
Total Quantity: 2,127,339 PCS (outdated data with tripled values)
```

### After Deployment:
```
Total Items: 1,085 (merged/deduplicated)
Total Quantity: 259,406 PCS (exact match with Excel)
```

---

## 🆘 TROUBLESHOOTING

### Error: "git pull fails"
```bash
# Discard local changes and pull again
git checkout -- .
git pull origin master
```

### Error: "Migrations fail"
```bash
# Check migration status
python manage.py showmigrations forms

# If stuck, check logs
tail -f /var/log/your-app.log
```

### Error: "Stock data not loaded"
```bash
# Load fixture manually
python manage.py loaddata stock_items

# Or reload from Excel
python manage.py load_akshay_stock --clear
```

### Error: "Page still shows old data"
```bash
# Clear Django cache
python manage.py clear_cache

# Restart web server
sudo systemctl restart deye-app

# Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
```

---

## 📝 LOG IMPORTANT INFO

After successful deployment, save this info:

```
✅ Deployment Date: [Date]
✅ Deployed Version: [git commit hash]
✅ Stock Items: 1,976
✅ Total Quantity: 259,406 PCS
✅ Data Verified: YES
✅ Sorting Fix: Applied (None serial handling)
✅ Blank Serial Items: Included (40 items)
```

Get commit hash:
```bash
git log -1 --oneline
# Example output: 0e9e7f4 docs: Add automated deployment scripts
```

---

## 🔗 GITHUB COMMITS DEPLOYED

When you pull master, these commits are included:

1. **b9e062a** - Complete stock management system
   - 1,976 stock items from Excel
   - Stock data fixture
   - Management command

2. **195e955** - Sorting TypeError fix
   - Handle None serial numbers
   - Verified with 1,085 merged items

3. **0e9e7f4** - Deployment automation
   - deploy.py script
   - deploy.sh script
   - DEPLOYMENT_GUIDE.md

---

## 📞 QUICK REFERENCE

| Task | Command |
|------|---------|
| Deploy (fastest) | `python deploy.py` |
| Just pull code | `git pull origin master` |
| Just run migrations | `python manage.py migrate` |
| Verify stock | `python manage.py shell` then `StockItem.objects.count()` |
| Restart app | `sudo systemctl restart deye-app` |
| Check logs | `tail -f /var/log/deye-app.log` |
| Test endpoint | `curl https://deycindia.in/stock/received/` |

---

## ✨ THAT'S IT!

Run ONE of:
- `python deploy.py` (Recommended)
- `./deploy.sh` (After editing path)
- Manual commands (If scripts fail)

Everything else is automated! 🎉

Questions? Check DEPLOYMENT_GUIDE.md for detailed instructions.
