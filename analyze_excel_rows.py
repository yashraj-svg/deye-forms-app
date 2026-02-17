"""
Analyze Current stock updated.xlsx to see all rows and why some are skipped
"""
import openpyxl
from pathlib import Path

excel_file = Path(__file__).parent / 'Current stock updated.xlsx'
wb = openpyxl.load_workbook(str(excel_file), data_only=True)
ws = wb['Current Stock']

print("=" * 100)
print(f"ANALYZING EXCEL FILE: Current Stock sheet")
print("=" * 100)

total_rows = 0
valid_rows = 0
skipped_rows = []

for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    if not row or all(cell is None or cell == '' for cell in row):
        continue
    
    total_rows += 1
    
    # Column mapping: B=Serial, C=Component, D=Description, E=Balance
    serial_number = row[1] if len(row) > 1 else None  # Column B (index 1)
    component_type = row[2] if len(row) > 2 else None  # Column C (index 2)
    description = row[3] if len(row) > 3 else None    # Column D (index 3)
    balance = row[4] if len(row) > 4 else None        # Column E (index 4)
    
    # Check why row would be skipped
    skip_reason = None
    
    if not balance or balance == 0:
        skip_reason = "No balance or zero"
    
    if skip_reason:
        skipped_rows.append({
            'row': row_idx,
            'serial': serial_number,
            'component': component_type,
            'description': description,
            'balance': balance,
            'reason': skip_reason
        })
    else:
        valid_rows += 1

print(f"\nTotal rows (excluding header): {total_rows}")
print(f"Valid rows (will be imported): {valid_rows}")
print(f"Skipped rows: {len(skipped_rows)}")

if skipped_rows:
    print(f"\n{'-' * 100}")
    print(f"ROWS THAT WILL BE SKIPPED ({len(skipped_rows)} rows):")
    print(f"{'-' * 100}")
    for item in skipped_rows[:20]:  # Show first 20
        print(f"Row {item['row']:4d}: Serial={item['serial']!s:30s} Component={item['component']!s:30s} Balance={item['balance']} -> {item['reason']}")
    
    if len(skipped_rows) > 20:
        print(f"... and {len(skipped_rows) - 20} more skipped rows")

wb.close()

print(f"\n{'-' * 100}")
print(f"SUMMARY:")
print(f"  Total rows in Excel (excluding header): {total_rows}")
print(f"  Rows that will be imported: {valid_rows}")
print(f"  Rows that will be skipped: {len(skipped_rows)}")
print(f"{'-' * 100}")
