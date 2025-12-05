import sys
from PyQt5.QtWidgets import QApplication
from Login_Ui_Window import LoginWindow
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


