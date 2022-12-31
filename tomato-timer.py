import sys
import os
import time
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


def resourcePath(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class App:
    __conf = {
        "appName": "Tomato Focus",
        "logDir": "local",
        "logFile": "tomato.log",
        "timeFocus": 25,
        "timeShortBreak": 5,
        "timeLongBreak": 15,
        "longBreakCount": 4,  # no. tomatos per long break
        "homepage": "https://github.com/yttty/tomato-timer"
    }
    __setters = ["timeFocus", "timeShortBreak", "timeLongBreak"]

    @staticmethod
    def config(name):
        return App.__conf[name]

    @staticmethod
    def set(name, value):
        if name in App.__setters:
            App.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)

        # seconds
        self.toolTipRefresh = 1

        self.tomatoCount = 0
        self.initMenu()
        self.initIcon()
        self.initTimer()
        self.initLogs()
        self.setStatus("idle")

        # self.messageClicked.connect(self.msgClicked)

    def initLogs(self):
        if not os.path.exists(resourcePath(App.config("logDir"))):
            os.mkdir(resourcePath(App.config("logDir")))

    def initIcon(self):
        """
        Init tray icon
        """
        self.iconIdle = QIcon(
            resourcePath(os.path.join("resources", "tomato-idle.svg")))
        self.iconFocus = QIcon(
            resourcePath(os.path.join("resources", "tomato-focus.svg")))
        self.iconRest = QIcon(
            resourcePath(os.path.join("resources", "tomato-rest.svg")))

        self.notificationIcon = self.MessageIcon()
        self.activated.connect(self.iconClicked)  # 把鼠标点击图标的信号和槽连接

    def initMenu(self):
        """
        Init tray icon menu
        """
        self.focusAction = QAction(
            "Start Focus", self, triggered=self.startFocus)
        self.restAction = QAction(
            "Take a Rest", self, triggered=self.startRest)
        self.stopAction = QAction("Stop Timer", self, triggered=self.stopTimer)
        self.aboutAction = QAction("Homepage", self, triggered=self.homepage)
        self.quitAction = QAction("Exit", self, triggered=self.quit)

        self.idleMenu = QMenu()
        self.idleMenu.addActions(
            [self.focusAction, self.aboutAction, self.quitAction])

        self.focusMenu = QMenu()
        self.focusMenu.addActions(
            [self.restAction, self.stopAction, self.aboutAction, self.quitAction])

        self.restMenu = QMenu()
        self.restMenu.addActions(
            [self.focusAction, self.stopAction, self.aboutAction, self.quitAction])

    def initTimer(self):
        """
        Init timer
        """
        self.tomatoTimer = QTimer(self)
        self.tomatoTimer.timeout.connect(self.tomato)
        self.toolTipTimer = QTimer(self)
        self.toolTipTimer.timeout.connect(self.updateToolTip)
        # Hover on the tray icon to show remaining time
        self.toolTipTimer.start(self.toolTipRefresh * 1000)

    def updateToolTip(self):
        """
        Hover on the tray icon to show tool tips (remaining time, timer status)
        """
        if self.status == "idle":
            self.setToolTip("Timer Stopped")
        elif self.status == "focus":
            minute, second = self.getRemainingTime()
            self.setToolTip(
                f"Focus remaining {minute}m{second}s\n{self.tomatoCount} consecutive tomatos!")
        elif self.status == "rest":
            minute, second = self.getRemainingTime()
            self.setToolTip(
                f"Rest remainig {minute}m{second}s\n{self.tomatoCount} consecutive tomatos!")

    def notify(self, content):
        self.showMessage(App.config("appName"), content, self.notificationIcon)

    def iconClicked(self, reason):
        """
        Handle tray icon click event

        Params
        ======
            reason: A integer signal will be transmitted upon clicking tray icon
                * 1 right click
                * 2 left double click
                * 3 left click
                * 4 middle click
        """
        # print(reason)
        if reason == 2:
            if self.status == 'idle' or self.status == 'rest':
                self.startFocus()
            else:
                self.startRest()

    def getRemainingTime(self):
        second = int(self.tomatoTimer.remainingTime() / 1000)
        minute = int(second / 60)
        second = int(second % 60)
        return minute, second

    def getRestTime(self):
        """
        Calculate time for next rest
        """
        if self.tomatoCount != 0 and self.tomatoCount % App.config("longBreakCount") == 0:
            return App.config("timeLongBreak") * 60 * 1000
        else:
            return App.config("timeShortBreak") * 60 * 1000

    def setStatus(self, status: str):
        if status == "idle":
            self.status = status
            self.setIcon(self.iconIdle)
            self.setContextMenu(self.idleMenu)
        elif status == "focus":
            self.status = status
            self.setIcon(self.iconFocus)
            self.setContextMenu(self.focusMenu)
        elif status == "rest":
            self.status = status
            self.setIcon(self.iconRest)
            self.setContextMenu(self.restMenu)
        else:
            raise ValueError("Invalid status.")

    def startFocus(self):
        """
        Set the duration of focus and start focus
        """
        self.tomatoTimer.start(App.config("timeFocus") * 60 * 1000)
        self.setStatus("focus")
        self.notify(f"Focus {App.config('timeFocus')} minutes")

    def startRest(self):
        """
        Set the duration of rest and start rest
        """
        rt = self.getRestTime()
        self.tomatoTimer.start(rt)
        self.setStatus("rest")
        self.notify(f"Rest {int(rt/(60*1000))} minutes")

    def tomato(self):
        if self.status == "focus":
            self.tomatoCount += 1
            self.startRest()
        elif self.status == 'rest' or self.status == "idle":
            self.startFocus()
        else:
            raise ValueError("Invalid status.")

    def recordTomato(self):
        if self.tomatoCount > 0:
            with open(resourcePath(os.path.join(App.config("logDir"), App.config("logFile"))),
                      'a+') as fout:
                fout.write(
                    f"{QDateTime.currentDateTime().toString(Qt.ISODateWithMs)},{self.tomatoCount}\n"
                )
            self.tomatoCount = 0

    def stopTimer(self):
        self.tomatoTimer.stop()
        if self.status == "focus" or self.status == "rest":
            self.recordTomato()
        self.setStatus("idle")

    def homepage(self):
        webbrowser.open(App.config("homepage"))

    def quit(self):
        """
        Safe exit
        """
        self.stopTimer()
        self.setVisible(False)
        self.parent().close()
        qApp.quit()
        sys.exit()


class TomatoFocus(QWidget):
    def __init__(self, parent=None):
        super(TomatoFocus, self).__init__(parent)
        self.ti = TrayIcon(self)
        self.ti.show()


def main():
    app = QApplication(sys.argv)
    w = TomatoFocus()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
