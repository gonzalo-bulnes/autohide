import sys
from typing import List, NewType, Union

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Magic values.
SEPARATOR = "separator"


class AutoHideMenuBar(QMenuBar):
    """A menu bar that hides itself automatically when out of focus."""
    def __init__(self) -> None:
        super().__init__()
        self.hide()

    def focusOutEvent(self, event: QFocusEvent) -> bool:
        """Hide the menu bar unless the focus went to a menu."""
        if event.reason() != Qt.PopupFocusReason:
            self.hide()
        return super().focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Show the menu bar and grab focus when Alt is pressed. Close it on Alt or Escape."""
        if event.key() == Qt.Key_Alt:
            if self.isVisible():
                self.hide()
                self.clearFocus()
                return None
            else:
                self.show()
                self.setFocus()
                return None
        if event.key() == Qt.Key_Escape:
            self.hide()
            self.clearFocus()
            return None
        return super().keyPressEvent(event)


class Main(QMainWindow):
    """The application main window."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUI()

    def setupUI(self) -> None:
        self.setWindowTitle("Autohide")
        self.resize(600, 400)
        self.centralWidget = QLabel("Press Alt to show the menu bar.")
        # Ensure that something (anything) else than the menu bar can grab the focus.
        self.centralWidget.setFocusPolicy(Qt.StrongFocus)
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)

        appActions = self.__createAppActions()
        _addActions(self, appActions)

        menubar = AutoHideMenuBar()
        self.setMenuBar(menubar)

        appMenu = QMenu("&Application", menubar)
        _addActions(appMenu, appActions)
        menubar.addMenu(appMenu)

        helpMenu = QMenu("&Help", menubar)
        helpMenu.addSection("For illustration only")
        menubar.addMenu(helpMenu)
        _addActions(helpMenu, appActions)

    def __createAppActions(self) -> None:
        quitAction = QAction("&Quit", self)
        quitAction.setIcon(QIcon.fromTheme("application-exit"))
        quitAction.setShortcut(QKeySequence.Quit)
        quitAction.triggered.connect(self.close)
        return [
                quitAction,
        ]

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Ensure the menu bar receives the event that will open it initially."""
        if event.key() == Qt.Key_Alt:
            self.menuBar().keyPressEvent(event)
        return super().keyPressEvent(event)

def _addActions(parent: QMenu, actions: List[Union[QAction, str]]) -> None:
    """Add actions to a menu or toolbar, add separator if action is None."""
    for action in actions:
        if action is SEPARATOR:
            action = QAction(parent)
            action.setSeparator(True)
        parent.addAction(action)

app = QApplication(sys.argv)

# Periodically listen for Unix signals (e.g. SIGINT)
timer = QTimer()
timer.start(500)
timer.timeout.connect(lambda: None)

window = Main()
window.show()
sys.exit(app.exec())
