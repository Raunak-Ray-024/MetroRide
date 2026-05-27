import psycopg2
from config.database import conn

class Drivers:

    def __init__(self, name, license_number, vehicle_type, phone_number, is_available):

        self.name = name
        self.license_number = license_number
        self.vehicle_type = vehicle_type
        self.phone_number = phone_number
        self.is_available = is_available

    # CREATE TABLE
    def create_table(self):

        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS drivers(

                driver_id SERIAL PRIMARY KEY,

                name VARCHAR(100) NOT NULL,

                license_number VARCHAR(50) UNIQUE NOT NULL,

                vehicle_type VARCHAR(50),

                phone_number VARCHAR(15),

                is_available BOOLEAN DEFAULT TRUE
            )
        """)

        conn.commit()

        print("Drivers table created successfully!")

    # INSERT DRIVER
    def insert_driver(self):

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO drivers
            (name, license_number, vehicle_type, phone_number, is_available)

            VALUES (%s, %s, %s, %s, %s)
        """, (

            self.name,
            self.license_number,
            self.vehicle_type,
            self.phone_number,
            self.is_available

        ))

        conn.commit()

        print("Driver inserted successfully!")

    # UPDATE DRIVER
    def update_driver(self, driver_id):

        cur = conn.cursor()

        cur.execute("""
            UPDATE drivers

            SET
                name=%s,
                license_number=%s,
                vehicle_type=%s,
                phone_number=%s,
                is_available=%s

            WHERE driver_id=%s
        """, (

            self.name,
            self.license_number,
            self.vehicle_type,
            self.phone_number,
            self.is_available,
            driver_id

        ))

        conn.commit()

        if cur.rowcount > 0:
            print("Driver updated successfully!")
        else:
            print("Driver not found!")

    # DELETE DRIVER
    def delete_driver(self, driver_id):

        cur = conn.cursor()

        cur.execute("""
            DELETE FROM drivers
            WHERE driver_id=%s
        """, (driver_id,))

        conn.commit()

        if cur.rowcount > 0:
            print("Driver deleted successfully!")
        else:
            print("Driver not found!")

    # GET ONE DRIVER
    def get_one_driver(self, driver_id):

        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM drivers
            WHERE driver_id=%s
        """, (driver_id,))

        driver = cur.fetchone()

        if driver:
            print(driver)
        else:
            print("Driver not found!")

    # GET ALL DRIVERS
    def get_all_drivers(self):

        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM drivers
        """)

        drivers = cur.fetchall()

        if drivers:

            for driver in drivers:
                print(driver)

        else:
            print("No drivers found!")


# DRIVER MENU
def driver_menu():

    while True:

        print("\n===== DRIVER MENU =====")

        print("1. Create Drivers Table")
        print("2. Insert Driver")
        print("3. Update Driver")
        print("4. Delete Driver")
        print("5. View One Driver")
        print("6. View All Drivers")
        print("7. Exit")

        choice = input("Enter your choice: ")

        # CREATE TABLE
        if choice == "1":

            driver = Drivers("", "", "", "", True)

            driver.create_table()

        # INSERT DRIVER
        elif choice == "2":

            name = input("Enter Driver Name: ")

            license_number = input("Enter License Number: ")

            vehicle_type = input("Enter Vehicle Type: ")

            phone_number = input("Enter Phone Number: ")

            available = input("Is Driver Available? (yes/no): ").lower()

            if available == "yes":
                is_available = True
            else:
                is_available = False

            driver = Drivers(
                name,
                license_number,
                vehicle_type,
                phone_number,
                is_available
            )

            driver.insert_driver()

        # UPDATE DRIVER
        elif choice == "3":

            driver_id = int(input("Enter Driver ID to Update: "))

            name = input("Enter New Driver Name: ")

            license_number = input("Enter New License Number: ")

            vehicle_type = input("Enter New Vehicle Type: ")

            phone_number = input("Enter New Phone Number: ")

            available = input("Is Driver Available? (yes/no): ").lower()

            if available == "yes":
                is_available = True
            else:
                is_available = False

            driver = Drivers(
                name,
                license_number,
                vehicle_type,
                phone_number,
                is_available
            )

            driver.update_driver(driver_id)

        # DELETE DRIVER
        elif choice == "4":

            driver_id = int(input("Enter Driver ID to Delete: "))

            driver = Drivers("", "", "", "", True)

            driver.delete_driver(driver_id)

        # VIEW ONE DRIVER
        elif choice == "5":

            driver_id = int(input("Enter Driver ID: "))

            driver = Drivers("", "", "", "", True)

            driver.get_one_driver(driver_id)

        # VIEW ALL DRIVERS
        elif choice == "6":

            driver = Drivers("", "", "", "", True)

            driver.get_all_drivers()

        # EXIT
        elif choice == "7":

            print("Exiting Driver Menu...")

            break

        else:

            print("Invalid Choice! Please try again.")


if __name__ == "__main__":

    driver_menu()