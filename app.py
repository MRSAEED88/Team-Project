import sys
from PyQt5.QtWidgets import QApplication
from gui.login import LoginDialog
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    login = LoginDialog()
    result = login.exec_()

    if result == login.Accepted:
        window = MainWindow(
            user_id=login.user_id,
            user_role=login.user_role,
            user_name=login.user_name
        )
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
