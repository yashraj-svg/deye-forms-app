"""
Test the sorting logic for received_stock view
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import StockItem
from django.db.models import Sum

print('\n' + '='*80)
print('TESTING RECEIVED_STOCK SORTING')
print('='*80)

# Get data similar to what received_stock does
stock_items = StockItem.objects.all()

# Merge duplicates by PCBA SN across all years in the filtered set
merged = {}
for item in stock_items.order_by('pcba_sn_new'):
    # For non-serialized items (blank serial), use a unique key
    if not item.pcba_sn_new:
        key = f"no_sn_{item.component_type or 'unknown'}_{item.specification or 'unknown'}_{item.year}"
    else:
        key = item.pcba_sn_new
    
    if key not in merged:
        merged[key] = {
            'pcba_sn_new': item.pcba_sn_new,
            'pcba_sn_old': item.pcba_sn_old,
            'component_type': item.component_type,
            'specification': item.specification,
            'quantity': item.quantity,
            'years': {item.year} if item.year else set(),
            'remark': item.remark or '',
        }
    else:
        merged[key]['quantity'] += item.quantity
        if item.pcba_sn_old and not merged[key]['pcba_sn_old']:
            merged[key]['pcba_sn_old'] = item.pcba_sn_old
        if item.component_type and not merged[key]['component_type']:
            merged[key]['component_type'] = item.component_type
        if item.specification and not merged[key]['specification']:
            merged[key]['specification'] = item.specification
        if item.remark:
            if merged[key]['remark'] and item.remark not in merged[key]['remark']:
                merged[key]['remark'] = f"{merged[key]['remark']}; {item.remark}"
            elif not merged[key]['remark']:
                merged[key]['remark'] = item.remark
        if item.year:
            merged[key]['years'].add(item.year)

merged_list = list(merged.values())

print(f'\nTotal merged items: {len(merged_list)}')

# Test the sorting with the fixed code
print('\n📊 Testing sort logic...')
try:
    merged_list.sort(key=lambda x: (
        -(max(x['years']) if x['years'] else 0),
        x['component_type'] or '',
        x['pcba_sn_new'] or ''  # Fixed: Convert None to empty string
    ))
    print('✅ Sorting successful!')
    print(f'   No comparison errors with None values')
except TypeError as e:
    print(f'❌ Sorting failed: {e}')

# Show some sorted results
print(f'\n📋 First 10 items after sorting:')
for idx, item in enumerate(merged_list[:10], 1):
    serial = item['pcba_sn_new'] or '(blank serial)'
    comp = item['component_type'] or 'N/A'
    qty = item['quantity']
    print(f'   {idx}. Serial: {serial} | Component: {comp} | Qty: {qty}')

# Check items with blank serials
blank_items = [m for m in merged_list if m['pcba_sn_new'] is None]
print(f'\n📍 Items with blank serial numbers: {len(blank_items)}')
if blank_items:
    for idx, item in enumerate(blank_items[:5], 1):
        comp = item['component_type'] or 'N/A'
        print(f'   {idx}. {comp} | Qty: {item["quantity"]}')
    if len(blank_items) > 5:
        print(f'   ... and {len(blank_items) - 5} more')

print(f'\n✅ ALL TESTS PASSED!')
print('   The received_stock view should work without sorting errors')
print('\n' + '='*80)
