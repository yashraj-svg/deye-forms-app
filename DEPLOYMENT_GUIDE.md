# 🚀 Deployment Guide - Update Web Server

This guide explains how to deploy the latest stock management updates to your production server.

## 📋 What Will Be Deployed

### Changes from GitHub:
- ✅ Complete stock management system (1,976 items)
- ✅ Fixed sorting error (None serial number handling)
- ✅ Allow NULL serial numbers for non-serialized items
- ✅ Auto-load stock data from fixture
- ✅ Management command for Excel imports

### Data Updates:
- **1,976 stock items** with exact quantities
- **259,406 PCS** total inventory
- **Perfect match** with Excel file
- **Covers**: 2020-2025 years

---

## 🔧 Deployment Methods

### Method 1: Python Script (Recommended - Cross-Platform)

**On your server:**

```bash
# Navigate to your project
cd /path/to/deye-forms-app

# Run the deployment script
python deploy.py

# Or specify project path
python deploy.py /path/to/deye-forms-app
```

**What it does:**
1. Pulls latest code from GitHub
2. Installs dependencies
3. Runs migrations (auto-loads stock data)
4. Collects static files
5. Verifies data integrity

---

### Method 2: Bash Script (Linux/Mac)

**On your server:**

```bash
# Make script executable
chmod +x deploy.sh

# Edit the script and update PROJECT_DIR
nano deploy.sh
# Change: PROJECT_DIR="/path/to/deye-forms-app"

# Run deployment
./deploy.sh
```

---

### Method 3: Manual Steps (If scripts don't work)

**SSH into your server:**

```bash
# 1. Navigate to project
cd /path/to/deye-forms-app

# 2. Pull latest code
git fetch origin
git pull origin master

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations (auto-loads stock data)
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Restart web server
sudo systemctl restart deye-app
# OR if using gunicorn/uwsgi - restart accordingly

# 8. Verify deployment
python -c "
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'deye_config.settings'
django.setup()
from forms.models import StockItem
print(f'Items: {StockItem.objects.count()}')
"
```

---

## 📝 For Windows Server / IIS

**PowerShell (as Administrator):**

```powershell
# Navigate to project
cd C:\path\to\deye-forms-app

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Pull latest code
git pull origin master

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart IIS application pool
Restart-WebAppPool -Name "DeyeApp"
```

---

## ✅ Verification Steps

After deployment, verify everything works:

### Check 1: Database
```bash
python manage.py shell
>>> from forms.models import StockItem
>>> StockItem.objects.count()  # Should be 1976
>>> from django.db.models import Sum
>>> StockItem.objects.aggregate(total=Sum('quantity'))['total']  # Should be 259406
```

### Check 2: Web Page
```bash
# Check locally first
curl http://localhost:8000/stock/received/

# Then check production
curl https://deycindia.in/stock/received/
```

Should show:
- **Total Items**: 1,085 (merged)
- **Total Quantity**: 259,406 PCS
- **No sorting errors**

### Check 3: Sample Items
On the web page, verify you can see:
- Items with serial numbers (e.g., 30220405000018)
- Items with blank serials (Tools, fixtures, etc.)
- Correct quantities per item
- No duplicate entries

---

## 🔄 Automated Deployment (Optional)

### Using GitHub Actions (CI/CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ master ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Server
      env:
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      run: |
        mkdir -p ~/.ssh
        echo "$DEPLOY_KEY" > ~/.ssh/deploy_key
        chmod 600 ~/.ssh/deploy_key
        ssh-keyscan -H your-server.com >> ~/.ssh/known_hosts
        ssh -i ~/.ssh/deploy_key user@your-server.com 'cd /path/to/deye-forms-app && bash deploy.sh'
```

---

## 🛠️ Troubleshooting

### Issue: Git pull fails
```bash
# Clear local changes
git checkout -- .
git pull origin master
```

### Issue: Migrations fail
```bash
# Check migration status
python manage.py showmigrations

# Rollback one migration if needed
python manage.py migrate forms 0033

# Then run again
python manage.py migrate
```

### Issue: Stock data not loading
```bash
# Load fixture manually
python manage.py loaddata stock_items

# Or reload from Excel
python manage.py load_akshay_stock --clear
```

### Issue: Web page shows old data
```bash
# Clear Django cache
python manage.py clear_cache

# Restart web server
sudo systemctl restart deye-app

# Clear browser cache (Ctrl+Shift+Delete)
```

---

## 📊 Expected Results After Deployment

| Metric | Before | After |
|--------|--------|-------|
| Total Items | 552 (old, merged) | 1,085 (correct, merged) |
| Total Quantity | 2,127,339 (3x inflated) | 259,406 (correct) |
| Sorting Errors | ❌ Yes | ✅ No |
| Blank Serial Items | ❌ Missing | ✅ Included |
| Data Accuracy | ❌ Tripled values | ✅ Exact match |

---

## 📞 Support Commands

### Quick health check script:
```bash
#!/bin/bash
echo "Checking Deye App Status..."
echo ""
echo "1. Git status:"
cd /path/to/deye-forms-app
git status --short

echo ""
echo "2. Database status:"
python manage.py dbshell << EOF
SELECT COUNT(*) as stock_items FROM stock_items;
EOF

echo ""
echo "3. Web server status:"
sudo systemctl status deye-app --no-pager

echo ""
echo "✅ Health check complete"
```

---

## 📚 Related Documentation

- [Stock Management System](STOCK_PUSH_GUIDE.md)
- [Excel Import Command](forms/management/commands/load_akshay_stock.py)
- [Stock Data Fixture](forms/fixtures/stock_items.json)
- [Deployment Script](deploy.py)

---

## ❓ Questions?

See the error messages and troubleshoot accordingly. Most issues are resolved by:
1. Ensuring correct project path
2. Running migrations
3. Restarting web server
4. Clearing cache

For additional help, check the Django logs or contact your system administrator.
