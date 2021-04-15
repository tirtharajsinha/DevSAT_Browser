# importing required libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from qtwidgets import Toggle, AnimatedToggle
import os
import sys
import sqlite3


# main window
class BrowserWindow(QMainWindow):

    # constructor
    def __init__(self, *args, **kwargs):
        super(BrowserWindow, self).__init__()
        self.resize(1800, 1000)
        # creating a tab widget
        self.tabs = QTabWidget()

        # making document mode true
        self.tabs.setDocumentMode(True)

        # adding action when double clicked
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)

        # adding action when tab is changed
        self.tabs.currentChanged.connect(self.current_tab_changed)

        # making tabs closeable
        self.tabs.setTabsClosable(True)

        # adding action when tab close is requested
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        # making tabs as central widget
        self.setCentralWidget(self.tabs)

        # loding stylesheet
        f = open("style.css", "r")
        self.setStyleSheet(f.read())

        # connecting database
        self.conn = sqlite3.connect('static/devsat.db')
        # fetching data from database
        db_res = self.conn.execute("select * from devsat where id=1")
        result = db_res.fetchall()
        self.db_result = result[0]

        self.initui()

    def initui(self):

        self.tabs.setTabShape(QtWidgets.QTabWidget.Triangular)

        # creating a status bar

        self.status = QStatusBar()
        self.status.setFixedHeight(0)
        # self.topbar
        # setting status bar to the main window
        self.setStatusBar(self.status)

        # creating a tool bar for navigation
        navtb = QToolBar("Navigation")

        # adding tool bar tot he main window
        self.addToolBar(navtb)

        # creating back action
        back_btn = QAction(self)
        back_btn.setIcon(QIcon("static/back.png"))

        # setting status tip
        back_btn.setStatusTip("Back to previous page")

        # adding action to back button
        # making current tab to go back
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())

        # adding this to the navigation tool bar
        navtb.addAction(back_btn)

        # similarly adding next button
        next_btn = QAction(self)
        next_btn.setIcon(QIcon("static/front.png"))
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        # similarly adding reload button
        reload_btn = QAction(self)
        reload_btn.setIcon(QIcon("static/reload.png"))
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        # creating home action
        home_btn = QAction(self)
        home_btn.setIcon(QIcon("static/home.png"))
        home_btn.setStatusTip("Go home")

        # adding action to home button
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # adding a separator
        navtb.addSeparator()

        # creating a line edit widget for URL
        self.urlbar = QLineEdit()
        self.urlbar.setStyleSheet("border:1px solid white; border-radius:20px;")

        # adding action to line edit when return key is pressed
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        # adding line edit to tool bar
        navtb.addWidget(self.urlbar)

        # similarly adding save page action
        save_btn = QAction(self)
        save_btn.setIcon(QIcon("static/save.png"))
        save_btn.setStatusTip("Save current page as html")
        # save_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(save_btn)

        navtb.addSeparator()

        # similarly adding stop action
        stop_btn = QAction(self)
        stop_btn.setIcon(QIcon("static/close.png"))
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        navtb.addSeparator()

        # adding stop action
        login_btn = QAction(self)
        # login_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        if self.db_result[2] == "":
            login_btn.setIcon(QIcon("static/user-red.png"))
            login_btn.setText("log-in")
            login_btn.setStatusTip("log-in required")
        else:
            login_btn.setStatusTip("logged-in")
            login_btn.setIcon(QIcon("static/user-green.png"))
        navtb.addAction(login_btn)

        navtb.addSeparator()

        # adding settings button
        settings_btn = QAction(self)
        settings_btn.setIcon(QIcon("static/dots.png"))
        settings_btn.setStatusTip("personalize")
        settings_btn.triggered.connect(lambda: self.settingui())
        navtb.addAction(settings_btn)

        # creating first tab
        self.add_new_tab(QUrl('http://www.google.com'), 'Homepage')

        # showing all the components
        self.show()
        self.setWindowIcon(QIcon("static/devsat_x.png"))
        # setting window title
        self.setWindowTitle("    DEVSAT")

    # method for adding new tab
    def add_new_tab(self, qurl=None, label="Blank"):

        # if url is blank
        db_res = self.conn.execute("select * from devsat where id=1")
        result = db_res.fetchall()
        self.db_result = result[0]
        if self.db_result[4] == "google":
            qurl = QUrl('http://www.google.com')
        else:
            qurl = QUrl('http://www.bing.com')

        # creating a QWebEngineView object
        browser = QWebEngineView()

        # setting url to browser
        browser.setUrl(qurl)

        # setting tab index
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        # link=browser.page().contextMenuData().linkUrl()
        # adding action to the browser when url is changed
        # update the url
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        # adding action to the browser when loading is finished
        # set the tab title
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    # when double clicked is pressed on tabs
    def tab_open_doubleclick(self, i):

        # checking index i.e
        # No tab under the click
        if i == -1:
            # creating a new tab
            self.add_new_tab()

    # wen tab is changed
    def current_tab_changed(self, i):

        # get the curl
        qurl = self.tabs.currentWidget().url()

        # update the url
        self.update_urlbar(qurl, self.tabs.currentWidget())

        # update the title
        self.update_title(self.tabs.currentWidget())

    # when tab is closed
    def close_current_tab(self, i):

        # if there is only one tab
        if self.tabs.count() < 2:
            # do nothing
            return

        # else remove the tab
        self.tabs.removeTab(i)

    # method for updating the title
    def update_title(self, browser):

        # if signal is not from the current tab
        if browser != self.tabs.currentWidget():
            # do nothing
            return

        # get the page title
        title = self.tabs.currentWidget().page().title()

        # set the window title
        self.setWindowTitle("% s - DEVSAT" % title)

    # action to go to home
    def navigate_home(self):
        db_res = self.conn.execute("select * from devsat where id=1")
        result = db_res.fetchall()
        self.db_result = result[0]
        if self.db_result[4] == "google":
            # go to google
            qurl = QUrl('http://www.google.com')
        else:
            # go to bing
            qurl = QUrl('http://www.bing.com')

        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    # method for navigate to url
    def navigate_to_url(self):

        # get the line edit text
        # convert it to QUrl object
        q = QUrl(self.urlbar.text())

        # if scheme is blank
        if q.scheme() == "":
            # set scheme
            q.setScheme("http")

        # set the url
        self.tabs.currentWidget().setUrl(q)

    # method to update the url
    def update_urlbar(self, q, browser=None):

        # If this signal is not from the current tab, ignore
        if browser != self.tabs.currentWidget():
            return

        # set text to the url bar
        self.urlbar.setText(q.toString())

        # set cursor position
        self.urlbar.setCursorPosition(0)

    def settingui(self):
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        Dialog.exec_()


# settings dialog classes


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1000, 600)
        Dialog.setMinimumSize(800, 600)
        Dialog.setWindowTitle("SETTINGS")
        Dialog.setWindowIcon(QIcon("static/settings.png"))
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(0, 100, 800, 500))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setStyleSheet(u"background-color:rgb(60, 60, 60); color:white;")

        # loading css file
        f = open("dialog.css", "r")
        Dialog.setStyleSheet(f.read())

        # connecting database
        self.conn = sqlite3.connect('static/devsat.db')
        # fetching data from database
        db_res = self.conn.execute("select * from devsat where id=1")
        result = db_res.fetchall()
        self.db_result = result[0]

        # devsat logo
        self.imagedev = QtWidgets.QLabel(Dialog)
        self.imagedev.setGeometry(700, 10, 100, 100)
        self.imagedev.setAutoFillBackground(False)
        self.imagedev.setText("")
        self.imagedev.setPixmap(QtGui.QPixmap("static/devsat.png"))
        self.imagedev.setScaledContents(True)
        self.imagedev.setWordWrap(False)
        self.imagedev.setOpenExternalLinks(False)
        self.imagedev.setObjectName("devsat logo")

        # devsat branding
        self.devlab = QtWidgets.QLabel(Dialog)
        self.devlab.setGeometry(785, 40, 200, 40)
        self.devlab.setObjectName("settings")
        self.devlab.setText("DevSAT")
        self.devlab.setObjectName("head")
        self.devlab.setStyleSheet("color:#33cccc; letter-spacing:2px; font-size:40px;")

        # settings dialog heading
        self.set = QtWidgets.QLabel(Dialog)
        self.set.setGeometry(30, 65, 200, 30)
        self.set.setObjectName("settings")
        self.set.setText("Settings")
        self.set.setObjectName("head")
        self.set.setStyleSheet("color:#ffcc99; letter-spacing:2px; font-size:25px;")

        # personalized tab
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")

        # calling scrollbar

        # new tab lebel
        self.newtab = QtWidgets.QLabel(self.tab)
        self.newtab.setGeometry(QtCore.QRect(100, 10, 250, 40))
        self.newtab.setObjectName("label_2")
        self.newtab.setText("Set personalized newtab page")
        self.newtab.setObjectName("medium")

        # custom new Tab button
        self.radioButton = QtWidgets.QRadioButton(self.tab)
        self.radioButton.setGeometry(QtCore.QRect(200, 50, 200, 40))
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setText("Default newTab")

        self.radioButton_2 = QtWidgets.QRadioButton(self.tab)
        self.radioButton_2.setGeometry(QtCore.QRect(200, 90, 200, 40))
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_2.setText("Custom newtab")

        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(220, 160, 160, 30))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("custom tab page url :")
        self.label_2.setObjectName("medium")

        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setGeometry(QtCore.QRect(380, 150, 400, 40))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setPlaceholderText("https://google.com")

        # chech newtab button condition
        if self.db_result[3] == "":
            self.radioButton.setChecked(True)
        else:
            self.radioButton_2.setChecked(True)
            self.lineEdit.setText(self.db_result[3])

        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(100, 240, 170, 50)
        self.label_3.setObjectName("label_2")
        self.label_3.setText("Default Search Engine")
        self.label_3.setObjectName("medium")

        self.frame1 = QtWidgets.QFrame(self.tab)
        self.frame1.setGeometry(QtCore.QRect(100, 280, 300, 100))

        self.frame1.setObjectName("frame")

        self.google = QtWidgets.QRadioButton(self.frame1)
        self.google.setGeometry(QtCore.QRect(160, 10, 200, 40))
        self.google.setObjectName("google")
        self.google.setText("Google")

        self.bing = QtWidgets.QRadioButton(self.frame1)
        self.bing.setGeometry(QtCore.QRect(160, 60, 200, 40))
        self.bing.setObjectName("bing")
        self.bing.setText("Bing")

        # chech newtab button condition
        if self.db_result[4].lower() == "google":
            self.google.setChecked(True)
        else:
            self.bing.setChecked(True)

        self.save = QtWidgets.QPushButton(self.tab)
        self.save.setGeometry(QtCore.QRect(300, 400, 200, 50))
        self.save.setObjectName("save")
        self.save.setText("Save")
        self.save.setStyleSheet("color:cyan; font-size:18px; background:black; border-radius:8px;")
        self.save.clicked.connect(self.settab)
        self.save.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # adding to widget
        self.tabWidget.addTab(self.tab, "personalization")

        # profile page

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")

        # labeling heading
        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(50, 20, 300, 40))
        self.label.setObjectName("label")
        self.label.setText("Your Profile")
        self.label.setObjectName("head")

        # creating frame
        self.frame = QtWidgets.QFrame(self.tab_2)
        self.frame.setGeometry(QtCore.QRect(50, 80, 700, 200))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.frame.setStyleSheet("background-color:rgb(100,100,100);")

        # setting user image
        self.image = QtWidgets.QLabel(self.frame)
        self.image.setGeometry(20, 20, 150, 150)
        self.image.setAutoFillBackground(False)
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("static/user.png"))
        self.image.setScaledContents(True)
        self.image.setWordWrap(False)
        self.image.setOpenExternalLinks(False)
        self.image.setObjectName("user image")

        # placing username
        self.user = QtWidgets.QLabel(self.frame)
        self.user.setGeometry(QtCore.QRect(180, 40, 300, 30))
        self.user.setObjectName("username")
        self.user.setText(self.db_result[1])
        self.user.setObjectName("head")

        # creating login feedback label
        self.feed = QtWidgets.QLabel(self.frame)
        self.feed.setGeometry(QtCore.QRect(420, 45, 63, 20))
        self.feed.setObjectName("username")
        self.feed.setObjectName("badge")

        # placing email
        self.useremail = QtWidgets.QLabel(self.frame)
        self.useremail.setGeometry(QtCore.QRect(185, 70, 300, 40))
        self.useremail.setObjectName("username")
        self.useremail.setText(self.db_result[2])
        self.useremail.setObjectName("medium")

        # sign-up condition
        if self.db_result[2] == "":
            self.signup = QtWidgets.QPushButton(self.frame)
            self.signup.setGeometry(QtCore.QRect(500, 60, 150, 50))
            self.signup.setObjectName("pushButton_2")
            self.signup.setText("Sign in")
            self.signup.setObjectName("sign up")
            self.signup.setStyleSheet("background-color:#b3ffb3; color:black;")
            self.signup.clicked.connect(self.login)

            self.feed.setStyleSheet("background-color:red; color:black;")
            self.feed.setText("logged out")


        else:
            self.signout = QtWidgets.QPushButton(self.frame)
            self.signout.setGeometry(QtCore.QRect(500, 60, 150, 50))
            self.signout.setObjectName("pushButton_2")
            self.signout.setText("Sign out")
            self.signout.setObjectName("sign out")
            self.signout.setStyleSheet("border:1px solid white; border-radius:8px; color:white; font-size:20px;")
            self.signout.clicked.connect(self.logout)
            self.feed.setStyleSheet("background-color:green; color:black;")
            self.feed.setText("logged in")

        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(70, 10, 55, 16))
        self.label.setObjectName("label")
        self.label.setText("")

        self.pushButton = QtWidgets.QPushButton(self.tab_2)
        # self.pushButton.setGeometry(QtCore.QRect(180, 320, 200, 30))
        self.pushButton.move(100, 320)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Manage Account")
        self.pushButton.setObjectName("profile")
        self.pushButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.pushButton_2 = QtWidgets.QPushButton(self.tab_2)
        # self.pushButton_2.setGeometry(QtCore.QRect(180, 350, 200, 30))
        self.pushButton_2.move(100, 350)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("Sync")
        self.pushButton_2.setObjectName("profile")
        self.pushButton_2.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.pushButton_3 = QtWidgets.QPushButton(self.tab_2)
        # self.pushButton_3.setGeometry(QtCore.QRect(180, 350, 200, 30))
        self.pushButton_3.move(100, 380)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setText("Personal Info")
        self.pushButton_3.setObjectName("profile")
        self.pushButton_3.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.pushButton_4 = QtWidgets.QPushButton(self.tab_2)
        # self.pushButton_4.setGeometry(QtCore.QRect(180, 350, 200, 30))
        self.pushButton_4.move(100, 410)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setText("Profile preferences")
        self.pushButton_4.setObjectName("profile")
        self.pushButton_4.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # pushing tab_2 to widget
        self.tabWidget.addTab(self.tab_2, "Profiles")

        # privacy page
        self.privacy = QtWidgets.QWidget()
        self.privacy.setObjectName("privacy")

        self.label0 = QtWidgets.QLabel(self.privacy)
        self.label0.setGeometry(50, 20, 300, 40)
        self.label0.setObjectName("label")
        self.label0.setText("Privacy & Services")
        self.label0.setObjectName("head")

        # pushing privacy to widget
        self.tabWidget.addTab(self.privacy, "Privacy & Services")

        # about page
        self.about = QtWidgets.QWidget()
        self.about.setObjectName("devsat")

        # adding heading
        self.label = QtWidgets.QLabel(self.about)
        self.label.setGeometry(50, 20, 300, 40)
        self.label.setObjectName("label")
        self.label.setText("About")
        self.label.setObjectName("head")

        # devsat logo
        self.devlogo = QtWidgets.QLabel(self.about)
        self.devlogo.setGeometry(50, 80, 50, 50)
        self.devlogo.setAutoFillBackground(False)
        self.devlogo.setText("")
        self.devlogo.setPixmap(QtGui.QPixmap("static/devsat.png"))
        self.devlogo.setScaledContents(True)
        self.devlogo.setWordWrap(False)
        self.devlogo.setOpenExternalLinks(False)
        self.devlogo.setObjectName("devsat logo")

        # devsat branding
        self.abtdev = QtWidgets.QLabel(self.about)
        self.abtdev.setGeometry(100, 85, 200, 20)
        self.abtdev.setObjectName("settings")
        self.abtdev.setText("DevSAT Browser")
        self.abtdev.setObjectName("head")
        self.abtdev.setStyleSheet("color:white; letter-spacing:1px; font-size:22px;")

        # devsat version
        self.version = QtWidgets.QLabel(self.about)
        self.version.setGeometry(100, 110, 500, 20)
        self.version.setObjectName("settings")
        self.version.setText("Version Beta-1.0.0.2 (Official build) (64-bit)")
        self.version.setObjectName("head")
        self.version.setStyleSheet("color:white; letter-spacing:1px; font-size:14px")

        # devsat credential
        self.cred = QtWidgets.QLabel(self.about)
        self.cred.setGeometry(100, 200, 700, 20)
        self.cred.setObjectName("settings")
        self.cred.setText(
            "This browser is made possible by the Pyqt5 open source project and other open source Libraries.")
        self.cred.setObjectName("small")

        # devsat credential
        self.team = QtWidgets.QLabel(self.about)
        self.team.setGeometry(600, 400, 300, 20)
        self.team.setObjectName("settings")
        self.team.setText("- Built By DevSAT Team")
        self.team.setObjectName("small")
        self.team.setStyleSheet("color:cyan; font-size:18px")

        # pushing privacy to widget
        self.tabWidget.addTab(self.about, "About DevSAT")

        # self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        # seting tab icon

        self.tabWidget.setTabIcon(0, QIcon("static/custom.png"))
        self.tabWidget.setTabIcon(1, QIcon("static/profile.png"))
        self.tabWidget.setTabIcon(2, QIcon("static/shild.png"))
        self.tabWidget.setTabIcon(3, QIcon("static/devsat1.png"))

    def settab(self):

        if self.db_result[3] == "" and self.radioButton.isChecked():
            pass
        elif self.db_result[3] != "" and self.radioButton_2.isChecked():
            pass
        elif self.db_result[3] == "" and self.radioButton_2.isChecked():
            self.conn.execute("update devsat set newtab='{}' where id=1".format(self.lineEdit.text()))
        elif self.db_result[3] != "" and self.radioButton.isChecked():
            self.conn.execute("update devsat set newtab='' where id=1")

        if self.google.isChecked():
            self.conn.execute("update devsat set search='google' where id=1")
        else:
            self.conn.execute("update devsat set search='bing' where id=1")

        self.conn.commit()

    def login(self):
        print("login")
        winlog = QtWidgets.QDialog()
        ui = ui_winlog(winlog)

        winlog.show()
        winlog.exec_()

    def logout(self):
        self.conn.execute("update devsat set email='' where id=1;")
        self.conn.commit()


class ui_winlog(object):

    def __init__(self, dialog):
        dialog.setGeometry(200, 200, 500, 800)
        dialog.setFixedWidth(500)
        dialog.setFixedHeight(800)
        dialog.setWindowTitle("Sign-in")
        dialog.setWindowIcon(QIcon("static/user-green.png"))

        f = open("login.css", "r")

        dialog.setStyleSheet(f.read())
        dialog.setObjectName("head")

        self.initui(dialog)

    def initui(self, dialog):
        # head image
        self.image = QtWidgets.QLabel(dialog)
        self.image.setGeometry(140, 20, 240, 180)
        self.image.setAutoFillBackground(False)
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("static/devsat.png"))
        self.image.setScaledContents(True)
        self.image.setWordWrap(False)
        self.image.setOpenExternalLinks(False)
        self.image.setObjectName("image")

        # heading text
        self.head = QtWidgets.QLabel(dialog)
        self.head.move(180, 200)
        self.head.setText("welcome")
        self.head.setObjectName("head")
        self.head.adjustSize()

        # input fields
        self.nameinput = QLineEdit(dialog)
        self.nameinput.setGeometry(50, 280, 400, 50)
        self.nameinput.setPlaceholderText(" UserName")

        # input email
        self.emailinput = QLineEdit(dialog)
        self.emailinput.setGeometry(50, 350, 400, 50)
        self.emailinput.setPlaceholderText(" Email")

        # input password
        self.passinput = QLineEdit(dialog)
        self.passinput.setGeometry(50, 420, 400, 50)
        self.passinput.setPlaceholderText(" password")
        self.passinput.setEchoMode(QLineEdit.Password)

        # radio option1
        self.radiobtn1 = QRadioButton(dialog)
        self.radiobtn1.setGeometry(100, 550, 100, 20)
        self.radiobtn1.setText("Sign-in")
        self.radiobtn1.adjustSize()
        self.radiobtn1.setChecked(True)

        # radio option2
        self.radiobtn2 = QRadioButton(dialog)
        self.radiobtn2.setGeometry(300, 550, 100, 20)
        self.radiobtn2.setText("Register")
        self.radiobtn2.adjustSize()

        # submit button
        self.b1 = QtWidgets.QPushButton(dialog)
        self.b1.setText("SUBMIT")
        self.b1.setObjectName("btn1")
        self.b1.move(190, 650)
        self.b1.adjustSize()
        self.b1.clicked.connect(self.submit)

        # feedback lable
        self.feed = QLabel(dialog)
        self.feed.setGeometry(0, 750, 500, 50)
        self.feed.setText("")
        self.feed.setObjectName("feedback")

    def submit(self):
        conn = sqlite3.connect('static/devsat.db')
        # fetching data from database

        data = {}
        data["username"] = self.nameinput.text()
        data["email"] = self.emailinput.text()
        data["passward"] = self.passinput.text()
        if self.radiobtn1.isChecked():
            data["action"] = "sign-in"
            print(1)
            if data["username"] == "" or data["passward"] == "":
                self.feed.setStyleSheet("  background-color: yellowgreen;")
                self.feed.setText("Crendtial error")
            else:
                db_res = conn.execute("select * from admin")
                result = db_res.fetchall()
                print(len(result))
                if len(result) == 0:
                    self.feed.setStyleSheet("  background-color: yellowgreen;")
                    self.feed.setText("register Now")
                else:
                    print("done")
                    cred = conn.execute("select * from admin where id=1")
                    res = cred.fetchall()[0]
                    if res[2] == data["email"] and res[3] == data["passward"]:
                        conn.execute("update devsat set email='{}' where id=1".format(data["email"]))
                        conn.commit()
                        self.feed.setStyleSheet("  background-color: yellowgreen;")
                        self.feed.setText("logged in")
                    else:
                        self.feed.setStyleSheet("  background-color: yellowgreen;")
                        self.feed.setText("wrong credential")



        else:
            data["action"] = "register"
            if data["username"] == "" or data["passward"] == "" or data["email"] == "":
                self.feed.setStyleSheet("  background-color: yellowgreen;")
                self.feed.setText("Crendtial error")

            else:
                db_res = conn.execute("select * from admin where id=1")
                result = db_res.fetchall()
                if len(result) == 0:
                    conn.execute("INSERT INTO admin VALUES(1,'{}','{}','{}')".format(data["username"], data["email"],
                                                                                     data["passward"]))
                    conn.execute(
                        "update devsat set user='{}',email='{}' where id=1".format(data["username"], data["email"]))
                    self.feed.setStyleSheet("  background-color: yellowgreen;")
                    conn.commit()
                    self.feed.setText("Successfully registered")
                else:
                    self.feed.setStyleSheet("  background-color: yellowgreen;")
                    self.feed.setText("alreary registered")

        # if data["username"] == "" or data["passward"]=="":
        #     self.feed.setStyleSheet("  background-color: yellowgreen;")
        #     self.feed.setText("Error happen")
        # else:
        #     self.feed.setStyleSheet("  background-color: yellowgreen;")
        #     self.feed.setText("success")


# creating a PyQt5 application
app = QApplication(sys.argv)

# setting name to the application


# creating MainWindow object
window = BrowserWindow()

# loop
sys.exit(app.exec_())
