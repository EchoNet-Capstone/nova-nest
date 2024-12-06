from PyQt6.QtWidgets import QMenuBar, QMenu

class fileMenu(QMenu):
	def __init__(self):
		super().__init__()
		self.addMenu

class NestMenuBar(QMenuBar):
	def __init__(self):
		super().__init__()

		self.addMenu("File")
		self.addMenu("Help")