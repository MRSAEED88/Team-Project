from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import bcrypt
import sys

# IMPORTS
# Ensure these file names match exactly what you have in your folder
from student_dashboard import StudentDashboard
from admin_dashboard import AdminDashboard 

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KAU Login")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #e8f0ec;")

        # Main Layout
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left Panel (Image)
        self.left_panel = QtWidgets.QLabel()
        self.left_panel.setMinimumWidth(450)
        self.left_panel.setAlignment(QtCore.Qt.AlignCenter)
        
        # Try to load image, handle failure gracefully
        pix = QtGui.QPixmap("KAU ENGNEERING DEP.jpg")
        if not pix.isNull():
            self.left_panel.setPixmap(pix.scaled(550, 600, QtCore.Qt.KeepAspectRatioByExpanding))
        else:
            self.left_panel.setText("KAU Image Not Found")
            self.left_panel.setStyleSheet("background: #ccc; color: #333; font-weight: bold;")

        # Right Panel (Form)
        right_panel = QtWidgets.QFrame()
        right_panel.setFixedWidth(450)
        right_panel.setStyleSheet("background: white; border-top-right-radius: 40px; border-bottom-right-radius: 40px;")
        
        form_layout = QtWidgets.QVBoxLayout(right_panel)
        form_layout.setContentsMargins(60, 40, 60, 40)
        form_layout.setSpacing(20)

        # Title
        title = QtWidgets.QLabel("Log In")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #004E89;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        form_layout.addWidget(title)

        # Inputs
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Enter Email")
        self.email_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")

        form_layout.addWidget(QtWidgets.QLabel("Email"))
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(QtWidgets.QLabel("Password"))
        form_layout.addWidget(self.password_input)

        # Buttons
        self.login_btn = QtWidgets.QPushButton("Login")
        self.login_btn.setStyleSheet("background-color: #1E5631; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.login_btn.clicked.connect(self.login_user)
        
        form_layout.addWidget(self.login_btn)
        form_layout.addStretch()
        
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(right_panel)

    def login_user(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Fields cannot be empty.")
            return

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            # Check for user
            cur.execute("SELECT id, name, email, password, membership FROM users WHERE email=?", (email,))
            user = cur.fetchone()
            con.close()

            if user:
                user_id, name, db_email, pw_hash, membership = user
                
                # Verify password (handles bcrypt or plain text)
                if isinstance(pw_hash, str):
                    pw_hash = pw_hash.encode()
                
                try:
                    valid = bcrypt.checkpw(password.encode(), pw_hash)
                except ValueError:
                    # Fallback if password in DB is not hashed (plain text)
                    valid = (password == pw_hash.decode())

                if valid:
                    if membership == "admin":
                        self.dashboard = AdminDashboard(user_id)
                    else:
                        self.dashboard = StudentDashboard(user_id)
                    
                    self.dashboard.show()
                    self.close()
                else:
                    QMessageBox.warning(self, "Error", "Invalid Password")
            else:
                QMessageBox.warning(self, "Error", "User not found")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
