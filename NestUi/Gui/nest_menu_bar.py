from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction
from .nest_serial_gui import *
from ..Utils.gui_utils import *

class NestMenuBar(QMenuBar):
	def __init__(self):
		super().__init__()
		self.file_menu = QMenu(f'File')

		fm_options = {
						'save': (QAction(f'Save', self.file_menu), self.on_save),
						'open': (QAction(f'Open', self.file_menu), None),
						'exit': (QAction(f'Exit', self.file_menu), None),
						'order': ['save', 
								  'open', 
								  'sep', 
								  'exit']
					}

		add_menu_options(self.file_menu, fm_options)

		self.addMenu(self.file_menu)
		self.addMenu("Help")

		self.file_menu.actions()[0].triggered.connect(self.on_save)


	def on_save(self):
		self.save_widget = SerialPacketSender()
		self.save_widget.show()