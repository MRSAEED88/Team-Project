import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        
        uic.loadUi("MainWindow_UI.ui", self)

        
        self.leftmenu = self.findChild(QWidget, "leftmenu")
        self.sidebarList = self.findChild(QListWidget, "sidebarList")
        self.btnToggleMenu = self.findChild(QPushButton, "btnToggleMenu")

        
        self.stackedMain = self.findChild(QStackedWidget, "stackedMain")
        self.pageStudents = self.findChild(QWidget, "pageStudents")
        self.pageCourses = self.findChild(QWidget, "pageCourses")

        
        self.btnToggleMenu.clicked.connect(self.toggleMenu)

        
        self.populateSidebar()

        
        self.animation = QPropertyAnimation(self.leftmenu, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    
    #animation
    
    def toggleMenu(self):
        current_width = self.leftmenu.width()
        expanded = 220
        collapsed = 60

        if current_width == collapsed:
            target_width = expanded
        else:
            target_width = collapsed

        self.animation.stop()
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(target_width)
        self.animation.start()

    
    #full sidebar
    
    def populateSidebar(self):

        students = []
        courses = []

        self.sidebarList.addItem("=== Students ===")
        for s in students:
            self.sidebarList.addItem("• " + s)

        self.sidebarList.addItem("")
        self.sidebarList.addItem("=== Courses ===")
        for c in courses:
            self.sidebarList.addItem("• " + c)


