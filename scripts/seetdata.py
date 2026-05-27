# scripts/seed_data.py
import sys
import os

# This line ensures Python can find your config folder smoothly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db_connection

def seed_database():
    print("🌱 Starting database seeding...")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Open and read the SQL file
        sql_file_path = os.path.join('database', 'seed.sql')
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        # Execute the full script
        cursor.execute(sql_script)
        conn.commit()
        print("🎉 Success! Your database now has a mock dataset of Users and Drivers.")
    except Exception as e:
        conn.rollback()
        print("❌ Seeding failed:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_database()