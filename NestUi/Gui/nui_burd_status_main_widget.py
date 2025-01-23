from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from .StatusWidgets import *

class NestBurdStatusMainWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        burd_status_layout = QGridLayout(self)
        