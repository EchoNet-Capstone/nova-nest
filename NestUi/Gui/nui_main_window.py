from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt
from .nui_serial import *
from .nui_menu_bar import *
from .nui_main_widget import *

class NestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = NestMainWidget(self)
        self.menu_bar = NestMenuBar(self)

        self.init_ui()

        self.show_menu_action = QAction()
        self.show_menu_action.setShortcut("Ctrl+M") 
        self.show_menu_action.triggered.connect(self.toggle_menu_bar)
        
        self.addAction(self.show_menu_action)
        self.central_widget.burd_status.marker_released.connect(self.refresh_map)
        
    def init_ui(self):
        self.setMenuBar(self.menu_bar)
        self.menu_bar.hide()
        
        self.setCentralWidget(self.central_widget)

        # self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.burd_status)
        # self.burd_status.hide()

    def toggle_menu_bar(self):
        self.menu_bar.setVisible(not self.menu_bar.isVisible())
        
        self.setVisible(False)
        self.buoy_id = -1

    def refresh_map(self, buoy_id):
        # Implement the logic to refresh the map
        pass

        

