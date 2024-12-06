from PySide6.QtWidgets import QMenuBar, QMenu

class fileMenu(QMenu):
	def __init__(self, parent):
		super().__init__(parent)
		self.setTitle(f'File')
		self.addAction(f'Save')
		self.addAction(f'Open')
		self.addSeparator()
		self.addAction(f'Exit')

class NestMenuBar(QMenuBar):
	def __init__(self):
		super().__init__()
		self.addMenu(fileMenu(self))
		self.addMenu("Help")