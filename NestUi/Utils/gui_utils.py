from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

class NuiMenuOption():
    def __init__(self, widget, trigger_func, shortcut=None):
        self.widget:QWidget = widget
        self.trigger_func = trigger_func
        self.action:QAction = None
        self.shortcut = shortcut

        if widget:
            self.widget = self.widget()