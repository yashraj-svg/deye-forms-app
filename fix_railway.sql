-- Railway Database Fix SQL Script
-- Run this using: railway connect postgres
-- Then paste these commands one by one

-- Step 1: Check current state
\echo '=== CURRENT STATE (WRONG) ==='
SELECT COUNT(*) as total_items, SUM(quantity) as total_quantity FROM forms_stockitem;

-- Step 2: Delete ALL stock items
\echo '=== DELETING ALL STOCK ITEMS ==='
TRUNCATE TABLE forms_stockitem RESTART IDENTITY CASCADE;

-- Step 3: Verify deletion
\echo '=== VERIFYING DELETION ==='
SELECT COUNT(*) as remaining_items FROM forms_stockitem;

-- Step 4: Now run Django loaddata command from another terminal
\echo '=== NOW RUN THIS IN ANOTHER TERMINAL ==='
\echo 'railway run python manage.py loaddata stock_items'

-- Step 5: After fixture loads, verify
\echo '=== AFTER LOADING, RUN THIS TO VERIFY ==='
SELECT COUNT(*) as total_items, SUM(quantity) as total_quantity FROM forms_stockitem;
-- Should show: total_items: 1976, total_quantity: 259406
