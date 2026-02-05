# Local Testing Instructions for Bulk Paste Feature

## Setup
1. ✅ Server running at http://127.0.0.1:8000/
2. Navigate to: http://127.0.0.1:8000/stock/update-new-shipments/

## Test Case 1: Bulk Paste with Existing Serial Numbers

### Input:
**Serial Numbers (paste in left box):**
```
20110103100263
20110103100169
20110106100105
```

**Quantities (paste in right box):**
```
20
20
3
```

### Expected Result:
- ✅ All 3 rows added to table
- ✅ Component Type auto-filled (if serials exist in database)
- ✅ Description auto-filled (if serials exist in database)
- ✅ Quantities show: 20, 20, 3
- ✅ Success message appears: "✅ Added 3 items from bulk paste!"

---

## Test Case 2: Bulk Paste with Mix of Known & Unknown Serials

### Input:
**Serial Numbers:**
```
20110103100263
UNKNOWN_SERIAL_999
20110106100105
```

**Quantities:**
```
20
100
3
```

### Expected Result:
- ✅ Row 1: Serial filled, Component Type filled, Description filled, Qty: 20
- ✅ Row 2: Serial filled with "UNKNOWN_SERIAL_999", Component Type EMPTY, Description EMPTY, Qty: 100
- ✅ Row 3: Serial filled, Component Type filled, Description filled, Qty: 3
- ✅ User can edit Row 2's Component Type & Description manually
- ✅ Success message appears: "✅ Added 3 items from bulk paste!"

---

## Test Case 3: Validation - Mismatch Count

### Input:
**Serial Numbers:**
```
20110103100263
20110103100169
20110106100105
```

**Quantities:**
```
20
20
```

### Expected Result:
- ❌ Error message: "❌ Mismatch: 3 serial numbers but 2 quantities. They must be equal!"
- No rows added
- User can fix and try again

---

## Test Case 4: Empty Input

### Input:
- Both textareas empty

### Expected Result:
- ❌ Error message: "❌ Please enter at least one serial number and quantity."

---

## Test Case 5: Invalid Quantity

### Input:
**Serial Numbers:**
```
20110103100263
20110103100169
```

**Quantities:**
```
20
abc
```

### Expected Result:
- ❌ Error message: "❌ Row 2: Invalid quantity "abc""
- No rows added

---

## Test Case 6: Existing Manual Entry + Bulk Paste

### Step 1:
- Manually add 1 item using "+ Add Another Item" button
- Fill: Serial="MANUAL_001", Component Type="Manual Type", Description="Manual Desc", Qty=50

### Step 2:
- Click "📋 Bulk Paste"
- Paste:
  - Serials: 20110103100263, 20110103100169
  - Quantities: 20, 20

### Expected Result:
- ✅ Table now has 3 rows:
  - Row 1: MANUAL_001, Manual Type, Manual Desc, 50
  - Row 2: 20110103100263, (auto-filled), (auto-filled), 20
  - Row 3: 20110103100169, (auto-filled), (auto-filled), 20
- ✅ Total Qty Received: 90

---

## Test Case 7: Form Submission

### Action:
- Add items via bulk paste
- Click "Update Shipments"

### Expected Result:
- ✅ Redirects to confirmation page
- ✅ Shows all items
- ✅ Shows total quantity
- ✅ Can confirm and save

---

## Test Case 8: Remove Row After Bulk Paste

### Action:
- Bulk paste 3 items
- Click "Remove" button on middle row

### Expected Result:
- ✅ Middle row deleted
- ✅ Remaining 2 rows stay
- ✅ Total Qty Received updates correctly

---

## Verification Checklist

- [ ] "📋 Bulk Paste" button visible on page
- [ ] Clicking button opens modal with 2 textareas side-by-side
- [ ] Left textarea labeled "Serial Numbers"
- [ ] Right textarea labeled "Quantities"
- [ ] Row counts shown below each textarea
- [ ] Can copy/paste without issues
- [ ] All validation errors work correctly
- [ ] Success message appears after adding
- [ ] Rows added to table correctly
- [ ] Component Type & Description auto-filled from database
- [ ] Unknown serials still added with empty fields
- [ ] Manual entry still works alongside bulk paste
- [ ] Remove button works on bulk-pasted items
- [ ] Form submission works with bulk-pasted items

---

## Notes
- The bulk paste processes items sequentially with async/await
- Each serial is looked up individually in the database
- Component Type & Description come from the StockItem model
- Year is auto-set to 2026 unless you modify the hidden field
- All existing one-by-one functionality remains unchanged
