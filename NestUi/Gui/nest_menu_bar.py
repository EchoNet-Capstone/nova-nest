from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction
from .nest_serial_gui import *

class NestMenuBar(QMenuBar):
	def __init__(self):
		super().__init__()
		self.file_menu = QMenu(f'File')

		fm_options = {
						'save': (QAction(f'Save', self.file_menu), self.on_save),
						'open': (QAction(f'Open', self.file_menu), None),
						'sep0': None,
						'exit': (QAction(f'Exit', self.file_menu), None),
						'order': ['save', 'open', 'sep0', 'exit']
					}

		self.add_menu_options(self.file_menu, fm_options)

		self.addMenu(self.file_menu)
		self.addMenu("Help")

		self.file_menu.actions()[0].triggered.connect(self.on_save)

	def add_menu_options(self, menu: QMenu, options: dict):
		for key in options['order']:
			curr_val = options[key]
			if curr_val:
				curr_action:QAction = curr_val[0]
				action_slot = curr_val[1]
				
				if action_slot:
					curr_action.triggered.connect(action_slot)

				menu.addAction(curr_action)
			else:	# separator
				menu.addSeparator()

	def on_save(self):
		self.save_widget = SerialPacketSender()
		self.save_widget.show()