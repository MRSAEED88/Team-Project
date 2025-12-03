from PyQt5 import QtWidgets, QtGui, QtCore
import resfile
# def login_user(self):
#     import sqlite3
#     from PyQt5.QtWidgets import QMessageBox

#     # 1) Get input values
#     email = self.username_input.text()
#     password = self.password_input.text()

#     # 2) Connect to SQLite database
#     con = sqlite3.connect("User.db")
#     cur = con.cursor()

#     # 3) Execute search query for user
#     cur.execute("SELECT * FROM users WHERE email=? AND passWord=?", (email, password)
#     
#     user = cur.fetchone()

#     # 4) Close DB connection
#     con.close()

#     # 5) Check if user exists
#     if user is None:
#         QMessageBox.warning(self, "Login Failed", "Invalid Username or Password")
#         return

#     # 6) Extract user info (matching the users table structure)
#     user_id = user[0]
#     name = user[1]
#     membership = user[4]     # "student" or "admin"

#     QMessageBox.information(self, "Welcome", f"Welcome {name}!")

#     # 7) Redirect based on role
#     if membership == "student":
#         self.open_student_dashboard(user_id)

#     elif membership == "admin":
#         self.open_admin_dashboard(user_id)


class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("KAU Login")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #e8f0ec;")

        
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        
        self.left_panel = QtWidgets.QLabel()
        self.left_panel.setMinimumWidth(450)
        self.left_panel.setAlignment(QtCore.Qt.AlignCenter)

        pix = QtGui.QPixmap("KAU ENGNEERING DEP.jpg") 
        if not pix.isNull():
            pix = pix.scaled(550, 595,
                             QtCore.Qt.KeepAspectRatioByExpanding,
                             QtCore.Qt.SmoothTransformation)
            self.left_panel.setPixmap(pix)
        else:
            self.left_panel.setText("KAU Image\nNot Found")
            self.left_panel.setStyleSheet("""
                color: #555;
                font-size: 18px;
                font-weight: bold;
            """)

        
        right_panel = QtWidgets.QFrame()
        right_panel.setFixedWidth(450)
        right_panel.setStyleSheet("""
            QFrame {
                background: white;
                border-top-right-radius: 40px;
                border-bottom-right-radius: 40px;
            }
        """)

        login_layout = QtWidgets.QVBoxLayout(right_panel)
        login_layout.setContentsMargins(60, 40, 60, 40)
        login_layout.setSpacing(20)

        #Title
        title = QtWidgets.QLabel("Log In")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #004E89;
        """)
        login_layout.addWidget(title)
        login_layout.addSpacing(10)

        # Username
        username_label = QtWidgets.QLabel("Username")
        username_label.setStyleSheet("font-size: 14px; color: #555;")
        login_layout.addWidget(username_label)

        username = QtWidgets.QLineEdit()
        username.setPlaceholderText("Enter your Username")
        username.setFixedHeight(40)
        username.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #1E5631;
                font-size: 16px;
                padding-left: 4px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #004E89;
            }
        """)
        login_layout.addWidget(username)

        #Password
        password_label = QtWidgets.QLabel("Password")
        password_label.setStyleSheet("font-size: 14px; color: #555;")
        login_layout.addWidget(password_label)

        password = QtWidgets.QLineEdit()
        password.setPlaceholderText("Enter your password")
        password.setEchoMode(QtWidgets.QLineEdit.Password)
        password.setFixedHeight(40)
        password.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #1E5631;
                font-size: 16px;
                padding-left: 4px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #004E89;
            }
        """)
        login_layout.addWidget(password)

        login_layout.addSpacing(20)

        
        login_btn = QtWidgets.QPushButton("L o g   I n")
        login_btn.setFixedHeight(48)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E5631;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: #004E89;
            }
            QPushButton:pressed {
                background-color: #00335f;
            }
        """)
        login_layout.addWidget(login_btn)

        
        forgot = QtWidgets.QLabel("Forgot your Username or password?")
        forgot.setAlignment(QtCore.Qt.AlignCenter)
        forgot.setStyleSheet("font-size: 13px; color: #004E89;")
        login_layout.addWidget(forgot)

        login_layout.addStretch()

        
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(right_panel)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())


