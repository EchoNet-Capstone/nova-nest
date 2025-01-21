from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

class NuiMenuOption():
    def __init__(self, widget:QWidget, trigger_func:object, shortcut:str=None):
        self.widget: QWidget = widget
        self.trigger_func: object = trigger_func
        self.action: QAction = None
        self.shortcut: str = shortcut

        if widget:
            self.widget = self.widget()