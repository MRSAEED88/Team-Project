import sys
import sqlite3
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# --- IMPORT DASHBOARDS ---
from student_dashboard import StudentDashboard
from admin_dashboard import AdminDashboard


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KAU Portal | Secure Login")

        # Make the window start maximized
        self.resize(950, 600)
        self.showMaximized()  

        self.setAttribute(Qt.WA_TranslucentBackground)

        # MAIN LAYOUT (Split Screen)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Panels
        self.setup_left_panel()
        self.setup_right_panel()

    # -------------------------------------------------------
    def setup_left_panel(self):
        self.left_frame = QFrame()
        self.left_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-top-left-radius: 15px;
                border-bottom-left-radius: 15px;
            }
        """)

        layout = QVBoxLayout(self.left_frame)
        layout.setContentsMargins(40, 0, 40, 0)

        lbl_logo = QLabel("KAU")
        lbl_logo.setStyleSheet("color: white; font-size: 60px; font-weight: bold;")
        lbl_logo.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel("Course Registration\nSystem")
        lbl_title.setStyleSheet("color: #bdc3c7; font-size: 20px;")
        lbl_title.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(lbl_logo)
        layout.addWidget(lbl_title)
        layout.addStretch()

        lbl_footer = QLabel("Faculty of Engineering\nFall 2025")
        lbl_footer.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        lbl_footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_footer)
        layout.addSpacing(20)

        self.main_layout.addWidget(self.left_frame)

    # -------------------------------------------------------
    def setup_right_panel(self):
        self.right_frame = QFrame()
        self.right_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
            }
        """)

        layout = QVBoxLayout(self.right_frame)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(20)

        lbl_welcome = QLabel("Welcome Back")
        lbl_welcome.setStyleSheet("color: #2c3e50; font-size: 32px; font-weight: bold;")
        layout.addWidget(lbl_welcome)

        lbl_sub = QLabel("Please enter your details to sign in.")
        lbl_sub.setStyleSheet("color: #95a5a6; font-size: 14px;")
        layout.addWidget(lbl_sub)

        layout.addSpacing(20)

        input_style = """
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
        """

        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("University ID or Email")
        self.inp_user.setStyleSheet(input_style)
        layout.addWidget(self.inp_user)

        # PASSWORD
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Password")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setStyleSheet(input_style)
        self.inp_pass.returnPressed.connect(self.login_user)
        layout.addWidget(self.inp_pass)

        # LOGIN BUTTON
        self.btn_login = QPushButton("Sign In")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #3498db; }
            QPushButton:pressed { background-color: #1abc9c; }
        """)
        self.btn_login.clicked.connect(self.login_user)
        layout.addWidget(self.btn_login)

        layout.addStretch()
        self.main_layout.addWidget(self.right_frame)

    # -------------------------------------------------------
    # LOGIN LOGIC
    # -------------------------------------------------------
    def login_user(self):
        user_input = self.inp_user.text().strip()
        password = self.inp_pass.text().strip()

        if not user_input or not password:
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields.")
            return

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            query = """
                SELECT id, name, email, password, membership 
                FROM users 
                WHERE email=? OR CAST(id AS TEXT)=?
            """
            cur.execute(query, (user_input, user_input))
            user = cur.fetchone()

            if user:
                user_id, name, db_email, pw_hash, membership = user

                # Convert DB value to bytes
                if isinstance(pw_hash, str):
                    pw_bytes = pw_hash.encode()
                else:
                    pw_bytes = pw_hash

                # Password Check
                valid = False
                try:
                    valid = bcrypt.checkpw(password.encode(), pw_bytes)
                except:
                    valid = (password == pw_hash or password == pw_bytes.decode())

                if valid:
                    self.open_dashboard(user_id, name, db_email, membership)
                else:
                    QMessageBox.warning(self, "Access Denied", "Incorrect password.")
            else:
                QMessageBox.warning(self, "Access Denied", "User not found.")

            con.close()

        except Exception as e:
            QMessageBox.critical(self, "System Error", f"Database Error:\n{e}")

    # -------------------------------------------------------
    def open_dashboard(self, user_id, name, email, membership):
        """
        Opens the correct dashboard based on membership.
        """
        if membership.lower() == "admin":
            self.dashboard = AdminDashboard(user_id)
        else:
            self.dashboard = StudentDashboard(user_id)

        # --- THIS IS THE FIX ---
        # Changed from .show() to .showMaximized()
        self.dashboard.showMaximized() 
        self.close()


# -----------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = LoginWindow()
    # Ensure the login window itself starts maximized
    window.showMaximized() 
    sys.exit(app.exec_())
