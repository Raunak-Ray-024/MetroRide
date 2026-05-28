from config.database import get_db_connection

def create_new_user(name, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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

def register_new_driver(name, license_number, vehicle_type, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO drivers (name, license_number, vehicle_type, phone_number, is_available) 
            VALUES (%s, %s, %s, %s, TRUE) 
            RETURNING driver_id;
        """
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
        return True
    except Exception as e:
        conn.rollback()
        print("❌ Database Error:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def book_ride_auto(passenger_id, pickup, dropoff, fare):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Find ONE available driver with a row lock
        cursor.execute("""
            SELECT driver_id FROM drivers 
            WHERE is_available = TRUE 
            LIMIT 1 
            FOR UPDATE;
        """)
        result = cursor.fetchone()
        
        if not result:
            return None
            
        driver_id = result[0]
        
        # 2. Set driver availability status to false
        cursor.execute(
            "UPDATE drivers SET is_available = FALSE WHERE driver_id = %s;", 
            (driver_id,)
        )
        
        # 3. Create the booking record
        cursor.execute("""
            INSERT INTO bookings (passenger_id, driver_id, pickup_address, dropoff_address, fare, status)
            VALUES (%s, %s, %s, %s, %s, 'accepted')
            RETURNING booking_id;
        """, (passenger_id, driver_id, pickup, dropoff, fare))
        
        booking_id = cursor.fetchone()[0]
        
        conn.commit()
        return {"booking_id": booking_id, "driver_id": driver_id}
        
    except Exception as e:
        conn.rollback()
        print("❌ System Matching Error:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

def complete_ongoing_ride(booking_id, driver_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE bookings 
            SET status = 'completed' 
            WHERE booking_id = %s;
        """, (booking_id,))
        
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

def get_user_ride_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
        
        columns = [desc[0] for desc in cursor.description]
        ride_history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return ride_history
    except Exception as e:
        print("❌ Error fetching ride history:", e)
        raise e
    finally:
        cursor.close()
        conn.close()