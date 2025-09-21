from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QWidget, QDialog)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QPalette, QColor
from widgets.terminal import Terminal
from widgets.widgets import *
import os


class PyTerm(QApplication):
    def __init__(self):
        super().__init__([])
        self.name = 'PyTerm'
        self.author = 'manish404'
        self.version = '1.0.0'
        self.size = QSize(700, 500)

    def start(self):
        # building app
        self._build()

    def _build(self):
        self.win = QWidget()
        self.win.setStyleSheet('background-color: red;')
        self._set()
        self._getInitialValues()
        self._buildItems()
        self.win.show()
        self.exec_()

    def _getInitialValues(self):
        self.currentDir = os.getcwd()

    def _set(self):
        # setting window styles
        self.win.setWindowTitle(self.name)
        self.win.resize(self.size)
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setMinimumSize(500, 300)
        self.win.setStyleSheet('''
            background-color: black;
            border-radius: 100px;
        ''')
        flags = Qt.WindowFlags(Qt.FramelessWindowHint |
                               Qt.WindowStaysOnTopHint)
        self.win.setWindowFlags(flags)
        # app informtion
        self.setApplicationName(self.name)
        self.setApplicationDisplayName(self.name)
        self.setOrganizationName('manish404')
        # global styles
        self.setStyleSheet('''
            QToolTip {
                color: white;
            }

            QWidget {
                background-color: black;
            }
        ''')
        # handling-window-events
        self.win.mousePressEvent = self._mousePressEvent
        self.win.mouseReleaseEvent = self._mouseReleaseEvent

    def _mousePressEvent(self, event):
        self.win.setCursor(Qt.ClosedHandCursor)
        self.win.dragPos = event.globalPos()

    def _mouseReleaseEvent(self, event):
        self.win.setCursor(Qt.ArrowCursor)

    def _moveWindow(self, event):
        if event.buttons() == Qt.LeftButton:
            self.win.move(self.win.pos() +
                          event.globalPos() - self.win.dragPos)
            self.win.dragPos = event.globalPos()
            event.accept()

    def _buildItems(self):
        self.mainLayout = QVBoxLayout(self.win)
        self.__removeMargin(self.mainLayout)
        self.mainLayout.setSpacing(0)
        self._buildTopArea()
        self._buildMiddleArea()
        self._buildBottomArea()

    def _buildTopArea(self):
        self.topArea = QFrame()
        self.__setMinMaxH(32, self.topArea)
        layout = QHBoxLayout(self.topArea)
        self.__removeMargin(layout)
        #
        title = QLabel('PyTerm')
        title.setStyleSheet('color: white; font-size: 15px; padding: 0 5px;')
        layout.addWidget(title)
        IconButton('addTab.ico', layout, False, 'Add Tab', self._addTab)
        layout.addStretch()
        # current running command
        self.currentCommand = QLabel()
        self.currentCommand.setStyleSheet(
            'color: white; padding: 0 4px; font-size: 13px;')
        #  font-weight: bold;
        layout.addWidget(self.currentCommand)
        layout.addStretch()
        #
        IconButton('minimize.png', layout, True,
                   'Minimize', self.win.showMinimized)
        IconButton('maximize.png', layout, True,
                   'Maximize', self._restore)
        IconButton('close.ico', layout, True, 'Close', self.exit)
        #
        self.mainLayout.addWidget(self.topArea)
        # events
        self.topArea.mouseMoveEvent = self._moveWindow
        self.topArea.mouseDoubleClickEvent = lambda x: self.win.showNormal(
        ) if self.win.isMaximized() else self.win.showMaximized()

    def _buildMiddleArea(self):
        self.mid = QTabWidget()
        self.mid.setTabsClosable(True)
        self.mid.setStyleSheet('''
            QTabBar::tab {
                width: 60px;
                color: white;
                padding: 10px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }

            QTabBar::tab:selected {
                background: grey;
            }
        ''')
        self.mid.addTab(Terminal(), "Tab 1")
        self.mainLayout.addWidget(self.mid)

    def _buildBottomArea(self):
        frame = QFrame()
        self.__setMinMaxH(30, frame)
        layout = QHBoxLayout(frame)
        self.__removeMargin(layout)
        # widgets in bottom area
        currentFolder = QLabel(self.currentDir)
        currentFolder.setStyleSheet(
            'color: white; font-size: 13px; padding-left: 2px;')
        layout.addWidget(currentFolder)
        layout.addStretch()
        IconButton('addTab.ico', layout, False, 'Add Tab', self._addTab)
        IconButton('settings.ico', layout, False,
                   'Open Settings', self._openSettings)
        #
        self.mainLayout.addWidget(frame)
        # resizing widgets in bottom corners
        tL = QHBoxLayout()
        tL.addWidget(Resizer(self.win, 7, 4))
        tL.addStretch()
        tL.addWidget(Resizer(self.win, 7, 4))
        self.mainLayout.addLayout(tL)

    def __setMinMaxH(self, height, widget):
        widget.setMaximumHeight(height)
        widget.setMinimumHeight(height)

    def __removeMargin(self, layout):
        layout.setContentsMargins(0, 0, 0, 0)

    def _openSettings(self):
        print("[+] Opening settings.")

    def _addTab(self):
        self.mid.addTab(Terminal(), "Tab")

    def _restore(self):
        if self.win.isMaximized():
            self.win.showNormal()
        else:
            self.win.showMaximized()

    def showCurrentCommand(self, command):
        self.currentCommand.setText(command)


if __name__ == "__main__":
    app = PyTerm()
    app.start()
