from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt
from .nui_serial import *
from .nui_menu_bar import *
from .nui_main_widget import *
from .nui_burd_status_main_widget import NestBurdStatusDockWidget

class NestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = NestMainWidget(self)
        self.burd_status = NestBurdStatusDockWidget(self)
        self.menu_bar = NestMenuBar(self)

        self.init_ui()

        self.show_menu_action = QAction()
        self.show_menu_action.setShortcut("Ctrl+M") 
        self.show_menu_action.triggered.connect(self.toggle_menu_bar)
        
        self.addAction(self.show_menu_action)

    def init_ui(self):
        self.setMenuBar(self.menu_bar)
        self.menu_bar.hide()
        
        self.setCentralWidget(self.central_widget)

        self.central_widget.burd_map_overlay.map_view.web_page.marker_clicked.connect(self.burd_status.toggle_visible)
        self.central_widget.burd_map_overlay.map_view.web_page.markerlicked.connect(self.burd_status.update_status)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.burd_status)
        self.burd_status.hide()

    def toggle_menu_bar(self):
        self.menu_bar.setVisible(not self.menu_bar.isVisible())
        

        

