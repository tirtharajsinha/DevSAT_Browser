# importing required libraries
from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import random
import sys
import subprocess
import sqlite3
import requests
import datetime
import time
import io
import webbrowser

build_version = "Version V:1.0.3.4 LTS (Official build) (64-bit)"


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
        f = open("static/style.css", "r")
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
        back_btn.triggered.connect(self.tabback)

        # adding this to the navigation tool bar
        navtb.addAction(back_btn)

        # similarly adding next button
        next_btn = QAction(self)
        next_btn.setIcon(QIcon("static/front.png"))
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(self.tabforward)
        navtb.addAction(next_btn)

        # similarly adding reload button
        reload_btn = QAction(self)
        reload_btn.setIcon(QIcon("static/reload.png"))
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(self.tabReload)
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

        # added download menu
        downMenu = QMenu()
        downMenu.setStyleSheet(
            "background-color:rgb(80, 80, 80); width:400px; padding:10px; color:white; font-size:16px;")

        self.down = QAction(self)

        self.down.setText("no downloads")
        self.down.setStatusTip("Save current page as html")
        self.down.triggered.connect(lambda: self.settingui(5))
        downMenu.addAction(self.down)

        self.opend = QAction(self)
        self.opend.setText("")
        self.openpath = ""

        self.opend.setStatusTip("Save current page as html")
        self.opend.triggered.connect(lambda: self.openloc())
        downMenu.addAction(self.opend)

        save_btn = QToolButton()
        # tb_set.clicked.connect(self.on_click_set_value)
        save_btn.setIcon(QIcon("static/save.png"))
        # adding menu to nevbar
        save_btn.setMenu(downMenu)
        save_btn.setPopupMode(QToolButton.InstantPopup)
        navtb.addWidget(save_btn)

        # adding bookmark btn
        mark_btn = QAction(self)
        mark_btn.setIcon(QIcon("static/bookmark.png"))
        mark_btn.setStatusTip("bookmark")
        mark_btn.triggered.connect(self.loadstop)
        navtb.addAction(mark_btn)

        # similarly adding stop action
        stop_btn = QAction(self)
        stop_btn.setIcon(QIcon("static/close.png"))
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(self.loadstop)
        navtb.addAction(stop_btn)

        navtb.addSeparator()

        # adding login action
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

        # creating menu
        SettingMenu = QMenu()
        SettingMenu.setStyleSheet(
            "background-color:rgb(41, 40, 40); width:200px; padding:20px; color:white; font-size:20px;")

        # similarly adding save page action
        save_btn = QAction(self)
        save_btn.setIcon(QIcon("static/save.png"))
        save_btn.setText("Save page")
        save_btn.setStatusTip("Save current page as html")
        save_btn.triggered.connect(self.save_file)
        SettingMenu.addAction(save_btn)

        # adding print button
        print_btn = QAction(self)
        print_btn.setIcon(QIcon("static/print.png"))
        print_btn.setText("print")
        print_btn.setStatusTip("personalize")
        print_btn.triggered.connect(lambda: self.print())
        SettingMenu.addAction(print_btn)

        SettingMenu.addSeparator()
        # adding settings button
        settings_btn = QAction(self)
        settings_btn.setIcon(QIcon("static/setting.png"))
        settings_btn.setText("settings")
        settings_btn.setStatusTip("personalize")
        settings_btn.triggered.connect(lambda: self.settingui())
        SettingMenu.addAction(settings_btn)

        tool_btn = QToolButton()
        # tb_set.clicked.connect(self.on_click_set_value)
        tool_btn.setIcon(QIcon("static/dots.png"))

        tool_btn.setMenu(SettingMenu)
        tool_btn.setPopupMode(QToolButton.InstantPopup)
        navtb.addWidget(tool_btn)

        # creating first tab
        self.add_new_tab(qurl="None", label='Homepage')

        # showing all the components
        self.show()
        self.setWindowIcon(QIcon("static/devsat.png"))
        # setting window title
        self.setWindowTitle("    DEVSAT")

    # method for adding new tab
    def add_new_tab(self, qurl="None", label="Blank"):

        # if url is blank
        if qurl == "None":
            db_res = self.conn.execute("select * from devsat where id=1")
            result = db_res.fetchall()
            self.db_result = result[0]
            if self.db_result[4] == "google":
                qurl = QUrl('http://www.google.com')
            else:
                qurl = QUrl('http://www.bing.com')
        else:

            qurl = QUrl(qurl)
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

        browser.loadFinished.connect(lambda: self.savehistory(browser.page().url(), browser.page().title()))

        browser.page().profile().downloadRequested.connect(self._downloadRequested)

    # when double clicked is pressed on tabs
    def tab_open_doubleclick(self, i):

        # checking index i.e
        # No tab under the click
        if i == -1:
            # creating a new tab
            self.add_new_tab()

    # wen tab is changed
    def current_tab_changed(self, i):

        try:
            # get the curl
            qurl = self.tabs.currentWidget().url()

            # update the url
            self.update_urlbar(qurl, self.tabs.currentWidget())

            # update the title
            self.update_title(self.tabs.currentWidget())
        except Exception:
            pass

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
        try:
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
        except:
            pass

    # method for navigate to url
    def navigate_to_url(self):

        # get the line edit text
        # convert it to QUrl object
        q = QUrl(self.urlbar.text())

        # if scheme is blank
        if q.scheme() == "":
            # set scheme
            q.setScheme("https")

        # set the url
        try:
            self.tabs.currentWidget().setUrl(q)
        except:
            pass

    # method to update the url
    def update_urlbar(self, q, browser=None):

        # If this signal is not from the current tab, ignore
        if browser != self.tabs.currentWidget():
            return

        # set text to the url bar
        self.urlbar.setText(q.toString())

        # set cursor position
        self.urlbar.setCursorPosition(0)

    def tabReload(self):
        try:
            self.tabs.currentWidget().reload()
        except:
            pass

    def tabforward(self):
        try:
            self.tabs.currentWidget().forward()
        except:
            pass

    def tabback(self):
        try:
            self.tabs.currentWidget().back()
        except:
            pass

    def loadstop(self):
        try:
            self.tabs.currentWidget().stop()
        except:
            pass

    def savehistory(self, url, title):

        url = url.toString()

        restricted = ["http://www.google.com", "https://www.google.com/", "http://www.bing.com",
                      "https://www.bing.com/"]
        # storing history

        if url not in restricted:
            # print(url)
            # print(title)
            date = str(datetime.datetime.now().date())
            self.conn.execute("insert into history values(null,'{}','{}','{}')".format(title, url, date))
            self.conn.commit()

    def print(self):
        printer = QPrinter()

        painter = QtGui.QPainter()
        # setting capture window
        painter.begin(printer)
        screen = self.grab()
        painter.drawPixmap(0, 0, self.rect().height(), self.rect().width(), screen)
        painter.end()

    def save_file(self):

        url = self.tabs.currentWidget().url().toString()

        html = requests.get(url).text

        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "",
                                                  "Hypertext Markup Language (*.htm *html);;"
                                                  "All files (*.*)")
        try:
            if filename:
                with io.open(filename, "w", encoding="utf-8") as f:
                    f.write(html)
        except Exception as e:
            print(e)

    def _downloadRequested(self, item):  # QWebEngineDownloadItem
        try:
            try:
                initDownPath = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
                my_dir = QFileDialog.getExistingDirectory(
                    self,
                    "select a download location",
                    initDownPath,
                    QFileDialog.ShowDirsOnly
                )
            except:
                pass

            # my_dir = my_dir.replace("/", "\\")
            # if my_dir[-1] != "\\":
            #     my_dir = my_dir + "\\" + item.downloadFileName()
            # else:
            #     my_dir = my_dir + item.downloadFileName()
            #
            # print(my_dir)
            # item.setPath(my_dir)
            print('downloading to', item.path())
            item.accept()
            self.down.setText("downloaded... " + item.downloadFileName())

            fpath = "/".join(str(item.path()).split("/")[:-1])
            self.openpath = fpath
            item.finished.connect(self.download_finished)
        except Exception as e:
            print(str(e))

    def download_finished(self):
        print("successfully downloaded")
        self.opend.setText("show in folder")

    def openloc(self):
        if (self.openpath != ""):
            print("path ready")
            path = self.openpath
            if 'darwin' in sys.platform:
                subprocess.check_call(['open', '--', path])
            elif 'linux' in sys.platform:
                subprocess.check_call(['xdg-open', path])
            elif 'win' in sys.platform:
                subprocess.call('explorer '+path)

    def settingui(self, index=1):

        Dialog = QtWidgets.QWidget()
        ui = Ui_Dialog()
        if index > 0:
            ui.setupUi(Dialog, self, index)

        i = self.tabs.addTab(ui.thiswindow, "settings")
        self.tabs.setCurrentIndex(i)


# settings dialog classes


class Ui_Dialog(object):
    def setupUi(self, Dialog, browser, tabindex=1):
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(50, 100, 1200, 500))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setStyleSheet(u"background-color:rgb(50, 50, 50); color:white;")
        self.browser = browser
        # loading css file
        f = open("static/dialog.css", "r")
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
        self.set.setGeometry(70, 50, 200, 30)
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
            self.signup.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
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
            self.signout.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
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

        # privacy logo
        self.prilogo = QtWidgets.QLabel(self.privacy)
        self.prilogo.setGeometry(50, 80, 170, 100)
        self.prilogo.setAutoFillBackground(False)
        self.prilogo.setText("")
        self.prilogo.setPixmap(QtGui.QPixmap("static/privacy.png"))
        self.prilogo.setScaledContents(True)
        self.prilogo.setWordWrap(False)
        self.prilogo.setOpenExternalLinks(False)
        self.prilogo.setObjectName("devsat logo")

        # promice label
        name = self.db_result[1].split()
        self.abtpri = QtWidgets.QLabel(self.privacy)
        self.abtpri.setGeometry(210, 100, 500, 30)
        self.abtpri.setObjectName("settings")
        self.abtpri.setText("Hey " + name[0] + ", We value your privacy.")
        self.abtpri.setObjectName("head")
        self.abtpri.setStyleSheet("color:white; letter-spacing:1px; font-size:22px;")

        # policy version
        self.policy = QtWidgets.QLabel(self.privacy)
        self.policy.setGeometry(210, 130, 500, 60)
        self.policy.setObjectName("settings")
        self.policy.setText(
            "We always protect and respect your privacy,\nwhile giving you the transparency and control you deserve.")
        self.policy.setObjectName("small")
        self.policy.setStyleSheet("color:white; letter-spacing:1px; font-size:14px")

        # privacy logo
        self.track = QtWidgets.QLabel(self.privacy)
        self.track.setGeometry(100, 200, 600, 250)
        self.track.setAutoFillBackground(False)
        self.track.setText("")
        self.track.setPixmap(QtGui.QPixmap("static/policy.JPG"))
        self.track.setScaledContents(True)
        self.track.setWordWrap(False)
        self.track.setOpenExternalLinks(False)
        self.track.setObjectName("devsat logo")

        # pushing privacy to widget
        self.tabWidget.addTab(self.privacy, "Privacy Services")

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
        self.version.setText(build_version)
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

        # building history page
        self.history = QtWidgets.QWidget()
        self.history.setObjectName("devsat")

        # adding heading
        self.hislabel = QtWidgets.QLabel(self.history)
        self.hislabel.setGeometry(50, 20, 300, 40)
        self.hislabel.setObjectName("label")
        self.hislabel.setText("History")
        self.hislabel.setObjectName("head")

        # scroll bar
        history = self.conn.execute("select * from history;")
        result = history.fetchall()
        self.formLayout = QFormLayout()
        groupBox = QGroupBox("Your last 7 days history")
        if len(result) > 1:
            result = result[-1::-1]
        rowcount = 0
        for data in result:
            rowcount += 1

            url = data[2]
            title = data[1]
            if len(title) > 15:
                title = title[:15]
            his = QPushButton("  " + title)
            his.setIcon(QIcon("static/external-link.png"))
            his.setStyleSheet("font-size:18px; color:yellowgreen; padding:10px;")
            his.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            his.clicked.connect(lambda x, url=url: self.openhist(url))

            date = QLabel(data[3])
            date.setStyleSheet("font-size:18px; color:white; padding-top:10px;")

            id = data[0]
            delhis = QPushButton(" Clear history ")
            delhis.setStyleSheet("font-size:18px; color:red; padding:10px;")
            delhis.setIcon(QIcon("static/trash.png"))
            delhis.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            delhis.clicked.connect(lambda x, id=id, rowcount=rowcount: self.delhist(id, rowcount))

            widget = QWidget()
            layout_h = QHBoxLayout(widget)
            layout_h.addWidget(his)
            layout_h.addWidget(delhis)
            self.formLayout.addRow(date, widget)

        groupBox.setLayout(self.formLayout)
        scroll = QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(350)
        self.frame2 = QtWidgets.QFrame(self.history)
        self.frame2.setGeometry(50, 80, 800, 360)
        self.frame2.setObjectName("frame2")

        layout = QVBoxLayout(self.frame2)

        layout.addWidget(scroll)

        # adding cleare all butten

        self.cls = QPushButton(self.history)
        self.cls.setText(" clear all")
        self.cls.setIcon(QIcon("static/trash.png"))
        self.cls.setGeometry(640, 30, 200, 40)
        # self.cls.setStyleSheet("font-size:18px; color:red; padding:10px;")
        self.cls.setStyleSheet("QPushButton::hover{background-color:red;color:white;font-size:18px;padding:10px;}")
        self.cls.setObjectName("clearall")
        self.cls.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.cls.clicked.connect(lambda x, rowcount=rowcount: self.clsall(rowcount))

        # pushing history to widget
        self.tabWidget.addTab(self.history, "history")

        # adding download page
        self.download = QtWidgets.QWidget()
        self.download.setObjectName("download")
        # adding head label
        self.dlabel = QtWidgets.QLabel(self.download)
        self.dlabel.setGeometry(50, 20, 300, 40)
        self.dlabel.setObjectName("label")
        self.dlabel.setText("Downloads")
        self.dlabel.setObjectName("head")

        # pushing history to widget
        self.tabWidget.addTab(self.download, "Downloads")

        # self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(tabindex)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        # seting tab icon

        self.tabWidget.setTabIcon(0, QIcon("static/custom.png"))
        self.tabWidget.setTabIcon(1, QIcon("static/profile.png"))
        self.tabWidget.setTabIcon(2, QIcon("static/shild.png"))
        self.tabWidget.setTabIcon(3, QIcon("static/devsat1.png"))

        self.thiswindow = Dialog

    def openhist(self, url):

        self.browser.add_new_tab(qurl=url)

    def delhist(self, id, rowcount):
        try:
            self.conn.execute("delete from history where id ={}".format(id))
            self.conn.commit()
            self.formLayout.removeRow(rowcount - 1)
        except Exception as e:
            pass

    def clsall(self, rowcount):
        try:
            self.conn.execute("delete from history;")
            self.conn.commit()
            for i in range(rowcount):
                self.formLayout.removeRow(i)

        except:
            pass

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

        winlog = QtWidgets.QDialog()
        ui = ui_winlog(winlog)

        winlog.show()
        winlog.exec_()

    def logout(self):
        self.conn.execute("update devsat set email='' where id=1;")
        self.conn.commit()


class ui_winlog(object):

    def __init__(self, dialog):
        dialog.setGeometry(200, 200, 1000, 600)
        # dialog.setFixedWidth(500)
        # dialog.setFixedHeight(650)
        dialog.setWindowTitle("Sign-in")
        dialog.setWindowIcon(QIcon("static/user-green.png"))

        f = open("static/login.css", "r")

        dialog.setStyleSheet(f.read())
        dialog.setObjectName("head")

        self.initui(dialog)

    def initui(self, dialog):
        pass
        self.leftf = QtWidgets.QLabel(dialog)
        self.leftf.setGeometry(0, 0, 500, 600)
        loginbg = ["loginbg.jpg", "loginbg2.jpg", "loginbg3.jpg", "loginbg4.jpg"]
        bg = random.randint(0, 3)
        self.leftf.setStyleSheet("background-image:url('static/{}');".format(loginbg[bg]))
        # head image
        self.image = QtWidgets.QLabel(dialog)
        self.image.setGeometry(120, 150, 260, 190)
        self.image.setAutoFillBackground(False)
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("static/devsat.png"))
        self.image.setScaledContents(True)
        self.image.setWordWrap(False)
        self.image.setOpenExternalLinks(False)
        self.image.setObjectName("image")

        # # heading text
        self.head = QtWidgets.QLabel(dialog)
        self.head.move(90, 380)
        self.head.setText("WELCOME BACK")
        self.head.setObjectName("head")
        self.head.adjustSize()

        # # heading text right
        self.headr = QtWidgets.QLabel(dialog)
        self.headr.move(590, 50)
        self.headr.setText("Sign in/Sign up")
        self.headr.setObjectName("headr")
        self.headr.adjustSize()

        # input fields
        self.nameinput = QLineEdit(dialog)
        self.nameinput.setGeometry(550, 180, 400, 50)
        self.nameinput.setPlaceholderText(" UserName")

        # input email
        self.emailinput = QLineEdit(dialog)
        self.emailinput.setGeometry(550, 250, 400, 50)
        self.emailinput.setPlaceholderText(" Email")
        #
        # input password
        self.passinput = QLineEdit(dialog)
        self.passinput.setGeometry(550, 320, 400, 50)
        self.passinput.setPlaceholderText(" password")
        self.passinput.setEchoMode(QLineEdit.Password)
        #
        # radio option1
        self.radiobtn1 = QRadioButton(dialog)
        self.radiobtn1.setGeometry(600, 400, 100, 20)
        self.radiobtn1.setText("Sign-in")
        self.radiobtn1.adjustSize()
        self.radiobtn1.setChecked(True)

        # radio option2
        self.radiobtn2 = QRadioButton(dialog)
        self.radiobtn2.setGeometry(800, 400, 100, 20)
        self.radiobtn2.setText("Register")
        self.radiobtn2.adjustSize()
        #
        # submit button
        self.b1 = QtWidgets.QPushButton(dialog)
        self.b1.setText("SUBMIT")
        self.b1.setObjectName("btn1")
        self.b1.move(690, 450)
        self.b1.adjustSize()
        self.b1.clicked.connect(self.submit)
        self.b1.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        #
        # feedback lable
        self.feed = QLabel(dialog)
        self.feed.setGeometry(500, 550, 500, 50)
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

            if data["username"] == "" or data["passward"] == "":
                self.feed.setStyleSheet("  background-color: yellowgreen;")
                self.feed.setText("Crendtial error")
            else:
                db_res = conn.execute("select * from admin")
                result = db_res.fetchall()

                if len(result) == 0:
                    self.feed.setStyleSheet("  background-color: yellowgreen;")
                    self.feed.setText("register Now")
                else:

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


class welcome(QMainWindow):
    def __init__(self):
        super().__init__()

        # <MainWindow Properties>
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, 600, 400)
        self.bg.setStyleSheet("background-image:url('static/welcomebg.jpg')")

        self.image = QtWidgets.QLabel(self)
        self.image.setGeometry(150, 130, 300, 210)
        self.image.setAutoFillBackground(False)
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("static/devsat.png"))
        self.image.setScaledContents(True)
        self.image.setWordWrap(False)
        self.image.setOpenExternalLinks(False)
        self.image.setObjectName("image")
        self.image.setStyleSheet("background-image:None;")

        bar = QProgressBar(self)
        x = 25
        # setting geometry to progress bar
        bar.setGeometry(0, 390, 650, 10)
        # setting value to progress bar
        bar.setValue(x)
        self.show()
        for i in range(3):
            x += 25

            bar.setValue(x)
            time.sleep(1)


# creating a PyQt5 application
app = QApplication(sys.argv)

# setting name to the application
welcome = welcome()
welcome.close()

# creating MainWindow object
window = BrowserWindow()

# loop
sys.exit(app.exec_())
