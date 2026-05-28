import psycopg2
from config.database import conn

#  CHANGE TO THIS:
# from config.database import get_db_connection
# conn = get_db_connection()
# ... now your existing cursor code (like conn.cursor()) will work perfectly!

class Bookings:

    def __init__(
        self,
        passenger_id,
        driver_id,
        pickup_address,
        dropoff_address,
        fare,
        status="accepted"
    ):

        self.passenger_id = passenger_id
        self.driver_id = driver_id
        self.pickup_address = pickup_address
        self.dropoff_address = dropoff_address
        self.fare = fare
        self.status = status

    # CREATE TABLE
    def create_table(self):

        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookings (

                booking_id SERIAL PRIMARY KEY,

                passenger_id INT,

                driver_id INT,

                pickup_address VARCHAR(255),

                dropoff_address VARCHAR(255),

                fare NUMERIC(6,2),

                status VARCHAR(50) DEFAULT 'accepted',

                FOREIGN KEY (passenger_id)
                REFERENCES users(user_id),

                FOREIGN KEY (driver_id)
                REFERENCES drivers(driver_id)
            )
        """)

        conn.commit()

        print("Bookings table created successfully!")

    # INSERT BOOKING + DRIVER UNAVAILABLE
    def create_booking(self):

        cur = conn.cursor()

        # CHECK DRIVER AVAILABLE
        cur.execute("""
            SELECT is_available
            FROM drivers
            WHERE driver_id = %s
        """, (self.driver_id,))

        driver = cur.fetchone()

        if not driver:
            print("Driver not found!")
            return

        if driver[0] == False:
            print("Driver is already booked!")
            return

        # INSERT BOOKING
        cur.execute("""
            INSERT INTO bookings (
                passenger_id,
                driver_id,
                pickup_address,
                dropoff_address,
                fare,
                status
            )

            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            self.passenger_id,
            self.driver_id,
            self.pickup_address,
            self.dropoff_address,
            self.fare,
            self.status
        ))

        # UPDATE DRIVER AVAILABILITY
        cur.execute("""
            UPDATE drivers
            SET is_available = FALSE
            WHERE driver_id = %s
        """, (self.driver_id,))

        conn.commit()

        print("Booking created successfully!")
        print("Driver marked as unavailable!")

    # VIEW ALL BOOKINGS
    def get_all_bookings(self):

        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM bookings
        """)

        bookings = cur.fetchall()

        if bookings:

            for booking in bookings:
                print(booking)

        else:
            print("No bookings found!")

    # DELETE BOOKING + DRIVER AVAILABLE AGAIN
    def delete_booking(self, booking_id):

        cur = conn.cursor()

        # GET DRIVER ID
        cur.execute("""
            SELECT driver_id
            FROM bookings
            WHERE booking_id = %s
        """, (booking_id,))

        data = cur.fetchone()

        if not data:
            print("Booking not found!")
            return

        driver_id = data[0]

        # DELETE BOOKING
        cur.execute("""
            DELETE FROM bookings
            WHERE booking_id = %s
        """, (booking_id,))

        # MAKE DRIVER AVAILABLE AGAIN
        cur.execute("""
            UPDATE drivers
            SET is_available = TRUE
            WHERE driver_id = %s
        """, (driver_id,))

        conn.commit()

        print("Booking deleted successfully!")
        print("Driver is available again!")

def booking_menu():

    while True:

        print("\n===== BOOKING MENU =====")
        print("1. Create Booking Table")
        print("2. Create Booking")
        print("3. View All Bookings")
        print("4. Delete Booking")
        print("5. Exit")

        choice = input("Enter your choice: ")

        # CREATE TABLE
        if choice == "1":

            booking = Bookings(0, 0, "", "", 0)
            booking.create_table()

        # CREATE BOOKING
        elif choice == "2":

            passenger_id = int(input("Enter Passenger ID: "))
            driver_id = int(input("Enter Driver ID: "))

            pickup = input("Enter Pickup Address: ")
            dropoff = input("Enter Dropoff Address: ")

            fare = float(input("Enter Fare: "))

            booking = Bookings(
                passenger_id,
                driver_id,
                pickup,
                dropoff,
                fare
            )

            booking.create_booking()

        # VIEW ALL BOOKINGS
        elif choice == "3":

            booking = Bookings(0, 0, "", "", 0)
            booking.get_all_bookings()

        # DELETE BOOKING
        elif choice == "4":

            booking_id = int(input("Enter Booking ID: "))

            booking = Bookings(0, 0, "", "", 0)
            booking.delete_booking(booking_id)

        # EXIT
        elif choice == "5":

            print("Exiting Booking Menu...")
            break

        else:
            print("Invalid Choice!")
if __name__ == "__main__":
    booking_menu()