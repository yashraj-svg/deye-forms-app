# Bulk Paste Feature for Update Shipments

## What's New
Added a **"📋 Bulk Paste"** button to the Update New Shipments page that allows you to:

### Feature Overview
1. **Paste Serial Numbers** - One per line in left textarea
2. **Paste Quantities** - One per line in right textarea  
3. **Auto-Populate** - Component Type & Description auto-fill from database
4. **Add New Items** - If serial not found, creates empty item for you to fill
5. **Keep Manual Entry** - Existing one-by-one entry still works perfectly

## How to Use

### Step 1: Click "📋 Bulk Paste" Button
Opens a modal with two side-by-side textareas

### Step 2: Paste Serial Numbers
Paste your serial numbers in the LEFT box (one per line):
```
20110103100263
20110103100169
20110106100105
20110106100965
20120102100019
20120103100068
```

### Step 3: Paste Quantities  
Paste your quantities in the RIGHT box (one per line):
```
20
20
3
3
160
30
```

### Step 4: Click "Add All Items"
The system will:
- ✅ Validate that serial count = quantity count
- ✅ Look up each serial in database
- ✅ Auto-fill Component Type & Description
- ✅ Add new row to your form for each pair
- ✅ Show success message

### Step 5: Review & Submit
- Check that all data looks correct
- Edit any missing Component Types if needed
- Click "Update Shipments" to save

## What Happens If Serial Not Found
- ✅ Row is still added to form
- ⚠️ Component Type field is EMPTY (you fill it in)
- ⚠️ Description field is EMPTY (you fill it in)
- This item is created as new unique stock

## Current Logic (Unchanged)
- ✅ You can still add items one-by-one with "+ Add Another Item"
- ✅ You can still use "Add Unique Item" button
- ✅ Serial number auto-complete suggestions still work
- ✅ All existing features work exactly as before

## Validation
Before processing, the system checks:
- ✅ Serial numbers count matches quantities count
- ✅ Each quantity is a valid number (not text)
- ✅ At least one pair is provided

If validation fails:
- ❌ Error message shows what's wrong
- You can edit and try again

## Example Result
If you paste:
```
Serials:          | Quantities:
20110103100263   | 20
20110103100169   | 20  
UNKNOWN_SN       | 100
```

Result:
| Serial | Component Type | Description | Qty |
|--------|---|---|---|
| 20110103100263 | MCU (auto-filled) | 16-bit processor (auto-filled) | 20 |
| 20110103100169 | PCB (auto-filled) | Green PCB 10x10 (auto-filled) | 20 |
| UNKNOWN_SN | *(empty - you fill in)* | *(empty - you fill in)* | 100 |

## Browser Compatibility
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support  
- Safari: ✅ Full support
- Mobile: ⚠️ Works but small screen, desktop recommended

## Tips
- Copy serials from Excel column A, paste in left box
- Copy quantities from Excel column B, paste in right box
- Use Tab to switch between textareas
- Order matters! First serial paired with first quantity, etc.
- You can bulk paste multiple times in one session
