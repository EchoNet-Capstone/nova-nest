from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction
from .nui_serial import *
from ..Utils.gui_utils import *

class NestMenuBar(QMenuBar):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.is_fullscreen = False
    
        '''
        Top Level dictionary contains the menu bar menu title and it's submenu 
        dictionary
        
        Second level dictionary contains the submenus and their NuiMenuOption 
        initialization calls
        '''
        self.menu_widgets = {
            'File': 
            {
                'Save': 
                    NuiMenuOption(
                        SerialPacketSender, 
                        None),
                'Open': 
                    NuiMenuOption(
                        None,
                        None),
                'Exit': 
                    NuiMenuOption(
                        None,
                        self.parent.close,
                        "Ctrl+Q")
            },
            'View':
            {
                'Fullscreen' : 
                    NuiMenuOption(
                        None,
                        self.toggle_fullscreen,
                        "F11")  
            },
            'Help':
            {}
        }

        '''
        Top Level entries are tuples in order from left to right on the displayed
        menu bar
            
        Within the tuple, the first element is a key matching a top level dictionary 
        entry above, followed by a list of that menu's submenus. The list of 
        submenus contains keys matching the second level dictionary above, with a 
        non-matching key signifiying a separator in the displayed submenu. 
        '''
        self.menu_layout =  [
            ('File',
            [
                'Save',
                'Open',
                '----',
                'Exit'
            ]),
            ('View',
            [
                'Fullscreen'
            ]),
            ('Help',
            [

            ])
        ]
    
        self.init_ui()

    def init_ui(self):
        for menu in self.menu_layout:
            curr_menu_title = menu[0]
            curr_menu_order = menu[1]

            curr_menu = QMenu(curr_menu_title, self)

            curr_menu.triggered.connect(self.menu_clicked)

            for menu_opt in curr_menu_order:
                try:
                    curr_opt: NuiMenuOption= self.menu_widgets[curr_menu_title][menu_opt]

                    curr_opt.action = QAction(menu_opt, curr_menu)
                    
                    if curr_opt.shortcut:
                        curr_opt.action.setShortcut(curr_opt.shortcut)

                    curr_menu.addAction(curr_opt.action)

                except KeyError:
                    curr_menu.addSeparator()
            
            curr_menu.setStyleSheet("QMenu::item {padding: 2px 25px 2px 20px;}")
            self.addMenu(curr_menu)


    def menu_clicked(self, action:QAction):
        text = action.text()
        parent_text = action.parent().title()
        
        triggered = False

        curr_menu_opt = self.menu_widgets[parent_text][text]

        if curr_menu_opt.widget:
            curr_menu_opt.widget.show()
            triggered = True

        if curr_menu_opt.trigger_func:
            curr_menu_opt.trigger_func()
            triggered = True

        if not triggered:
            print(f'Widget or Action {text} hasn\'t been initialized yet!')
    
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.parent.showNormal()
        else:
            self.parent.showFullScreen()
            
        self.is_fullscreen = not self.is_fullscreen

