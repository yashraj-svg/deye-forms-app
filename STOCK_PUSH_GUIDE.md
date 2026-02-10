# Stock Data Management - GitHub Push Guide

## Summary of Changes Made

### 1. **Database Models** (forms/models.py)
- ✅ Modified `StockItem.pcba_sn_new` field to allow NULL values
- Reason: Some items (fixtures, tools, test equipment) don't have serial numbers
- Change: Added `blank=True, null=True` to the field

### 2. **View Updates** (forms/views.py)
- ✅ Fixed `received_stock()` view to properly handle blank serial items
- Before: All blank serial items were merged into single entries
- After: Each item with blank serial shows separately while serialized items are merged across years

### 3. **Database Migrations**
Created 2 new migrations:
- `0033_alter_stockitem_pcba_sn_new.py` - Allows NULL pcba_sn_new field
- `0034_load_stock_items.py` - Automatically loads stock fixture on first migration

### 4. **Stock Data Fixture** (forms/fixtures/stock_items.json)
- ✅ All 1,976 stock items exported to JSON fixture
- Size: 894 KB
- Auto-loads on migration (if table is empty)
- Includes: Serial numbers, component types, specifications, quantities for all years 2020-2025

### 5. **Management Command** (forms/management/commands/load_akshay_stock.py)
- ✅ Django management command to reload stock from Excel
- Usage: `python manage.py load_akshay_stock --clear`
- Required: Excel file "Akshay India Shipping List 2020 - 2025.xlsx" in project root

### 6. **Helper Scripts** (for reference, no need to push)
- check_excel.py - Inspect Excel structure
- check_blank_serials.py - Find items with blank serials
- compare_stock_with_excel.py - Verify database matches Excel
- create_fixture.py - Create the JSON fixture
- verify_stock_final.py - Final verification report

---

## How to Push to GitHub

### Step 1: Check What Will Be Committed
```bash
git status
```

### Step 2: Add the Important Changes
```bash
# Add database models
git add forms/models.py

# Add view updates
git add forms/views.py

# Add migrations
git add forms/migrations/0033_alter_stockitem_pcba_sn_new.py
git add forms/migrations/0034_load_stock_items.py

# Add stock data fixture (contains all 1,976 items)
git add forms/fixtures/stock_items.json

# Add management command for Excel loading
git add forms/management/commands/load_akshay_stock.py
```

Or add them all at once:
```bash
git add forms/models.py forms/views.py forms/migrations/0033_alter_stockitem_pcba_sn_new.py forms/migrations/0034_load_stock_items.py forms/fixtures/stock_items.json forms/management/commands/load_akshay_stock.py
```

### Step 3: Commit the Changes
```bash
git commit -m "fix: Implement complete stock management with Excel import and blank serial support

- Allow NULL serial numbers for non-serialized items (tools, fixtures, etc)
- Fix received_stock view to show blank serial items separately
- Add 1,976 stock items from 'Akshay India Shipping List 2020 - 2025.xlsx'
- Create stock_items.json fixture for easy deployment
- Add management command to reload stock from Excel file
- Auto-load stock data on first migration

Includes all items 2020-2025 with exact quantities and descriptions"
```

### Step 4: Push to GitHub
```bash
git push origin master
```

---

## What Happens on the Other Machine (or server)

### When pulling the changes:
```bash
git pull origin master
```

### When running migrations:
```bash
python manage.py migrate
```

This will:
1. ✅ Apply the model change (allows NULL serial numbers)
2. ✅ Automatically load all 1,976 stock items from `stock_items.json`
3. ✅ Database will match exactly with Excel data

### Alternative: Reload from Excel anytime
If you want to reload stock from the Excel file:
```bash
python manage.py load_akshay_stock --clear
```

---

## File Checklist for Push

✅ Forms/Models Changes:
- `forms/models.py` - Modified StockItem model

✅ View Changes:
- `forms/views.py` - Fixed received_stock view

✅ Migrations:
- `forms/migrations/0033_alter_stockitem_pcba_sn_new.py` - NEW
- `forms/migrations/0034_load_stock_items.py` - NEW

✅ Data:
- `forms/fixtures/stock_items.json` - NEW (894 KB, all 1,976 items)

✅ Management Command:
- `forms/management/commands/load_akshay_stock.py` - NEW

❌ Do NOT push (these are temporary):
- `check_excel.py` - Temporary analysis script
- `check_blank_serials.py` - Temporary analysis script
- `compare_stock_with_excel.py` - Temporary analysis script
- `create_fixture.py` - Temporary creation script
- `verify_stock_final.py` - Temporary verification script
- `Akshay India Shipping List 2020 - 2025.xlsx` - Source file (keep locally)

---

## Verification After Push

On the other machine, verify everything:
```bash
# Pull the changes
git pull origin master

# Run migrations (auto-loads stock data)
python manage.py migrate

# Verify stock data loaded
python manage.py shell
>>> from forms.models import StockItem
>>> StockItem.objects.count()  # Should be 1976
>>> StockItem.objects.aggregate(total=Sum('quantity'))  # Should be 259406 PCS
```

If you need to reload from Excel file:
```bash
python manage.py load_akshay_stock --clear
```

---

## Summary

Everything is ready to push! The database will automatically:
- ✅ Apply the model changes (allow NULL serial)
- ✅ Load all 1,976 stock items from fixture
- ✅ Display received stock correctly without duplicates
- ✅ Show exact quantities matching Excel file

All quantities and descriptions are preserved exactly as in the Excel file!
