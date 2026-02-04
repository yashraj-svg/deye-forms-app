import sqlite3
import csv

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
query = "SELECT pincode, city, state, global_cargo_region, is_oda, deliverable, safexpress_is_oda, bluedart_region FROM freight_pincode_data"
cursor.execute(query)

with open('forms/fixtures/pincode_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['pincode','city','state','global_cargo_region','is_oda','deliverable','safexpress_is_oda','bluedart_region'])
    writer.writerows(cursor.fetchall())

conn.close()
print('CSV exported successfully')
