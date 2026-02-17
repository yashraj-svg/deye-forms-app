import sqlite3
import os

# Path to your SQLite database
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Drop the employee_checkin table if it exists
    cursor.execute("DROP TABLE IF EXISTS employee_checkin")
    
    # Delete the migration record from django_migrations
    cursor.execute("DELETE FROM django_migrations WHERE app='forms' AND name='0039_checkinout'")
    
    conn.commit()
    print("✅ Successfully dropped employee_checkin table and removed migration record")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
