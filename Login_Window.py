import sys
import sqlite3
import smtplib
import random
import string
from email.mime.text import MIMEText
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

# --- IMPORT DASHBOARDS ---
from student_dashboard import StudentDashboard
from admin_dashboard import AdminDashboard


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KAU Portal | Secure Login")

        self.resize(950, 600)
        self.showMaximized()
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

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
        layout.setSpacing(20)

        layout.addStretch()

        # --- LOGO SECTION ---
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("kau_logo.png")
        
        if not pixmap.isNull():
            # Scale slightly larger for the login screen
            scaled = pixmap.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(scaled)
        else:
            # Fallback Text Logo if image missing
            img_label.setText("KAU")
            img_label.setStyleSheet("color: white; font-size: 60px; font-weight: bold;")
        
        layout.addWidget(img_label)
        # ----------------------------

        lbl_title = QLabel("ECE Registration\nSystem")
        lbl_title.setStyleSheet("color: #bdc3c7; font-size: 24px; font-weight:bold;")
        lbl_title.setAlignment(Qt.AlignCenter)
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

        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Password")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setStyleSheet(input_style)
        self.inp_pass.returnPressed.connect(self.login_user)
        layout.addWidget(self.inp_pass)

        self.btn_forgot = QPushButton("Forgot Password?")
        self.btn_forgot.setCursor(Qt.PointingHandCursor)
        self.btn_forgot.setStyleSheet("""
            QPushButton {
                background: transparent; 
                color: #3498db; 
                border: none; 
                font-size: 13px;
                text-align: right;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        self.btn_forgot.clicked.connect(self.handle_forgot_password)
        layout.addWidget(self.btn_forgot, alignment=Qt.AlignRight)

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
    # LOGIC: FORGOT PASSWORD (PLAIN TEXT UPDATE)
    # -------------------------------------------------------
    def handle_forgot_password(self):
        email, ok = QInputDialog.getText(self, "Password Recovery", "Enter your registered email address:")
        
        if not ok or not email:
            return

        email = email.strip()

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            
            # Check if email exists
            cur.execute("SELECT id, name FROM users WHERE email=?", (email,))
            user = cur.fetchone()
            
            if not user:
                con.close()
                QMessageBox.warning(self, "Error", "Email address not found.")
                return

            # Generate temporary password (8 chars)
            temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # STORE AS PLAIN TEXT (No Hash)
            cur.execute("UPDATE users SET password=? WHERE email=?", (temp_pass, email))
            con.commit()
            con.close()

            # Send Email
            if self.send_recovery_email(email, temp_pass):
                QMessageBox.information(self, "Success", f"A temporary password has been sent to {email}.")
            else:
                QMessageBox.warning(self, "Email Failed", f"Could not send email.\n\nDEMO MODE - Temporary Password: {temp_pass}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database Error: {e}")

    def send_recovery_email(self, recipient, temp_pass):
        SENDER_EMAIL = "recoveryee48@gmail.com" 
        SENDER_PASSWORD = "ioxf bdgy cwjp kkvr"   
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        
        if "your_project_email" in SENDER_EMAIL:
            return False

        msg = MIMEText(f"Hello,\n\nYour password reset request was received.\n\nYour Temporary Password is: {temp_pass}\n\nPlease log in and change your password immediately.\n\nRegards,\nECE Registration System")
        msg['Subject'] = "Password Recovery - ECE Portal"
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"SMTP Error: {e}")
            return False

    # -------------------------------------------------------
    # LOGIC: LOGIN (PLAIN TEXT CHECK)
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
                user_id, name, db_email, db_password, membership = user

                # PLAIN TEXT COMPARISON
                if password == db_password:
                    self.open_dashboard(user_id, name, db_email, membership)
                else:
                    QMessageBox.warning(self, "Access Denied", "Incorrect password.")
            else:
                QMessageBox.warning(self, "Access Denied", "User not found.")

            con.close()

        except Exception as e:
            QMessageBox.critical(self, "System Error", f"Database Error:\n{e}")

    def open_dashboard(self, user_id, name, email, membership):
        if membership.lower() == "admin":
            self.dashboard = AdminDashboard(user_id)
        else:
            self.dashboard = StudentDashboard(user_id)

        self.dashboard.showMaximized() 
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = LoginWindow()
    window.showMaximized() 
    sys.exit(app.exec_())
