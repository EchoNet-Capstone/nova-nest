from PySide6.QtGui import QAction
from PySide6.QtCore import QObject, SIGNAL, SLOT
from PySide6.QtWidgets import QMenu, QWidget, QLabel, QScrollBar

class NuiMenuOption():
	def __init__(self, widget, trigger_func):
		self.widget = widget
		self.action = None
		self.trigger_func = trigger_func

		if widget:
			self.widget = self.widget()