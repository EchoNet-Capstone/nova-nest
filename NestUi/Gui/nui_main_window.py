from PySide6.QtWidgets import QMainWindow
from .nui_serial import *
from .nui_menu_bar import *
from .nui_main_widget import *

class NestMainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.init_ui()
		
	def init_ui(self):
		self.setMenuBar(NestMenuBar())
		self.setCentralWidget(NestMainWidget())

