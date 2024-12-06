from PySide6.QtWidgets import QMainWindow, QMenuBar
from .nest_serial_gui import *
from .nest_menu_bar import *

class NestMainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.init_ui()

		self.show()
	
	def init_ui(self):

		self.setCentralWidget(SerialPacketSender())
		self.setMinimumSize(1280, 720)

		self.setMenuBar(NestMenuBar())
		self.centralWidget()
