import sqlite3
from users_db import setup_database, add_users

def create_default_admin():
    """
    Creates a default admin user in the database if one does not already exist.
    """
    setup_database() # Ensure the database and tables are set up

    admin_id = 1
    admin_name = "Admin"
    admin_email = "admin@kau.edu.sa"
    admin_pass_plain = "admin123"

    # Use the add_users class from users_db to insert the admin
    admin_user_data = (admin_id, admin_name, admin_email, admin_pass_plain, "admin")
    add_users(admin_user_data).insertData()
    print(f"Admin user '{admin_email}' created/ensured.")

if __name__ == "__main__":
    create_default_admin()