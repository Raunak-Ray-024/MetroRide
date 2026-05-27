# app/services.py
from config.database import get_db_connection

def book_ride(passenger_id, driver_id, pickup, dropoff, fare):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE drivers SET is_available = FALSE WHERE driver_id = %s;", (driver_id,))
        
        cursor.execute("""
            INSERT INTO bookings (passenger_id, driver_id, pickup_address, dropoff_address, fare)
            VALUES (%s, %s, %s, %s, %s);
        """, (passenger_id, driver_id, pickup, dropoff, fare))
        
        conn.commit()
        return True # Return True if successful
    except Exception as e:
        conn.rollback()
        print("❌ Database Error:", e)
        return False # Return False if it fails
    finally:
        cursor.close()
        conn.close()


# In app/services.py

def create_new_user(name, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Change "RETURNING id" to "RETURNING user_id"
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING user_id;", 
            (name, email)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except Exception as e:
        conn.rollback()
        print("❌ DB Error:", e)
        raise e  
    finally:
        cursor.close()
        conn.close()

# def update_driver_profile(driver_id, name, license_number,):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute(
#             "UPDATE drivers SET name = %s, license_number = %s WHERE driver_id = %s;",
#             (name, license_number, driver_id)
#         )
#         conn.commit()
#         return True
#     except Exception as e:
#         conn.rollback()
#         print("❌ DB Error:", e)
#         return False
#     finally:
#         cursor.close()
#         conn.close()

# Inside app/services.py

def register_new_driver(name, license_number, vehicle_type, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Update the SQL string to include the new columns
        query = """
            INSERT INTO drivers (name, license_number, vehicle_type, phone_number, is_available) 
            VALUES (%s, %s, %s, %s,TRUE) 
            RETURNING driver_id;
        """
        # Pass the variables into the execute command in the exact same order
        cursor.execute(query, (name, license_number, vehicle_type, phone_number))
        
        driver_id = cursor.fetchone()[0]
        conn.commit()
        return driver_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# app/services.py

def book_ride_auto(passenger_id, pickup, dropoff, fare):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Find ONE available driver (using FOR UPDATE to lock the row safely)
        cursor.execute("""
            SELECT driver_id FROM drivers 
            WHERE is_available = TRUE 
            LIMIT 1 
            FOR UPDATE;
        """)
        result = cursor.fetchone()
        
        # If no drivers are free, return None so the API can tell the user
        if not result:
            return None
            
        driver_id = result[0]
        
        # 2. Make that specific driver busy
        cursor.execute(
            "UPDATE drivers SET is_available = FALSE WHERE driver_id = %s;", 
            (driver_id,)
        )
        
        # 3. Create the booking with our auto-selected driver
        cursor.execute("""
            INSERT INTO bookings (passenger_id, driver_id, pickup_address, dropoff_address, fare, status)
            VALUES (%s, %s, %s, %s, %s, 'accepted')
            RETURNING booking_id;
        """, (passenger_id, driver_id, pickup, dropoff, fare))
        
        booking_id = cursor.fetchone()[0]
        
        # Commit all changes together safely
        conn.commit()
        return {"booking_id": booking_id, "driver_id": driver_id}
        
    except Exception as e:
        conn.rollback()
        print("❌ System Matching Error:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

# app/services.py

def complete_ongoing_ride(booking_id, driver_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Update the booking status to completed
        cursor.execute("""
            UPDATE bookings 
            SET status = 'completed' 
            WHERE booking_id = %s;
        """, (booking_id,))
        
        # 2. Free up the driver so they can get matched again
        cursor.execute("""
            UPDATE drivers 
            SET is_available = TRUE 
            WHERE driver_id = %s;
        """, (driver_id,))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("❌ Complete Ride Error:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

# app/services.py

def get_user_ride_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # We join bookings with drivers to get the driver's name and vehicle details
        query = """
            SELECT 
                b.booking_id,
                d.name AS driver_name,
                d.vehicle_type,
                b.pickup_address,
                b.dropoff_address,
                b.fare,
                b.status
            FROM bookings b
            LEFT JOIN drivers d ON b.driver_id = d.driver_id
            WHERE b.passenger_id = %s
            ORDER BY b.booking_id DESC;
        """
        cursor.execute(query, (user_id,))
        
        # This clever line converts raw SQL tuples into clean Python dictionaries
        columns = [desc[0] for desc in cursor.description]
        ride_history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return ride_history
    except Exception as e:
        print("❌ Error fetching ride history:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

from sqlalchemy.orm import Session
# Adjust this import to match wherever your Booking model class is defined inside app
from database.bookings import Bookings 

from config.database import get_db_connection

def get_ride_history_by_passenger(passenger_id: int):
    """
    Fetches past ride rows from PostgreSQL using raw psycopg2 queries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Replace 'bookings' and 'passenger_id' with your exact SQL column names if different
        query = "SELECT * FROM bookings WHERE passenger_id = %s ORDER BY id DESC;"
        cursor.execute(query, (passenger_id,))
        
        # This grabs all columns dynamically
        columns = [desc[0] for desc in cursor.description]
        trips = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return trips
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()