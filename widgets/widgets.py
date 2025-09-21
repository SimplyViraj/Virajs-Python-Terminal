from PyQt5.QtWidgets import QPushButton, QSizeGrip
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt


class Resizer(QSizeGrip):
    def __init__(self, parent, w, h):
        super().__init__(parent)
        self.setMaximumSize(w, h)
        self.setStyleSheet('background-color: transparent;')


class IconButton(QPushButton):
    def __init__(self, iconName, layout, small, tooltip, function):
        super().__init__()
        if iconName.endswith('.ico'):
            self.setIcon(QIcon(f'./assets/images/{iconName}'))
        elif iconName.endswith('.png'):
            self.setIcon(QIcon(QPixmap(f'./assets/images/{iconName}')))
        if small == True:
            self.setIconSize(QSize(20, 20))
        elif small == False:
            self.setIconSize(QSize(25, 25))
        if tooltip and tooltip != '':
            self.setToolTip(tooltip)
        self.setStyleSheet(
            'border: none;')
        self.setCursor(Qt.ArrowCursor)

        if function:
            self.clicked.connect(function)
        layout.addWidget(self)
