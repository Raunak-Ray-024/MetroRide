import psycopg2
from config.database import conn

class Customer:
    def __init__(self,name,email,rating,is_active):
        self.name=name
        self.email=email
        self.rating=rating
        self.is_active=is_active
    def create_table(self):
        cur=conn.cursor()
        cur.execute(
            """ CREATE TABLE IF NOT EXISTS  users (
                    user_id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    rating NUMERIC(3, 2) DEFAULT 5.00,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )"""
        )
        conn.commit()
        cur.close()

    def insert_user(self,name,email,rating,is_active):
        cur=conn.cursor()
        cur.execute(
           """INSERT INTO users(name,email,rating,is_active)VALUES(%s,%s,%s,%s)""",(name, email, rating, is_active)
        )
        conn.commit()
        conn.close()
    
    def update_user(self,user_id,name=None,email=None, rating=None, is_active=None):
        cur=conn.cursor()
        cur.execute("SELECT * FROM user WHERE user_id=%s",(user_id,))
        user=cur.fetchone()
        if not user:
            print("user not found")
            cur.close()
            return
        update_fields = []
        if name:
            update_fields.append(f"name='{name}'")
        if email:
            update_fields.append(f"email='{email}'")
        if rating:
            update_fields.append(f"rating={rating}")
        if is_active is not None:
            update_fields.append(f"is_active={is_active}")
        update_query=f"UPDATE users SET{','.join(update_fields)} WHERE user_id=%s"
        cur.execute(update_query,(user_id,))
        conn.commit()
        cur.close()
    
    def delete_user(self,user_id):
        cur=conn.cursor()
        cur.execute(
            "DELETE FROM users WHERE user_id=%s,)",(user_id)
        )
        conn.commit()
        cur.close()

    def get_all_users(self):
        cur = conn.cursor()

        cur.execute("SELECT * FROM users")

        users = cur.fetchall()

        if not users:
            print("No users found")
        else:
            for user in users:
                print(user)

        cur.close()
    
def user_menu():

    customer = Customer("", "", 0, True)

    while True:

        print("\n===== USER MENU =====")
        print("1. Create Table")
        print("2. Insert User")
        print("3. Update User")
        print("4. Delete User")
        print("5. View All Users")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":

            customer.create_table()
            print("Table created successfully")

        elif choice == "2":

            name = input("Enter name: ")
            email = input("Enter email: ")
            rating = float(input("Enter rating: "))
            is_active = input("Is active? (True/False): ")

            is_active = is_active.lower() == "true"

            customer.insert_user(
                name,
                email,
                rating,
                is_active
            )

            print("User inserted successfully")

        elif choice == "3":

            user_id = int(input("Enter user id: "))

            name = input("Enter new name (leave blank to skip): ")
            email = input("Enter new email (leave blank to skip): ")

            rating_input = input(
                    "Enter new rating (leave blank to skip): "
                )

            active_input = input(
                    "Enter active status True/False (leave blank to skip): "
                )

            rating = float(rating_input) if rating_input else None

            is_active = (
                active_input.lower() == "true"
                if active_input else None
                )

            customer.update_user(
                user_id,
                name if name else None,
                email if email else None,
                rating,
                is_active
                )

        elif choice == "4":

            user_id = int(input("Enter user id: "))

            customer.delete_user(user_id)

        elif choice == "5":

            customer.get_all_users()

        elif choice == "6":

            print("Exiting...")
            break

        else:

            print("Invalid choice")
if __name__ == "__main__":
    user_menu()
