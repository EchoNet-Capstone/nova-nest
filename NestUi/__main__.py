import sys
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication
from dotenv import load_dotenv

from .Gui import NestMainWindow
from .Utils.nest_db import *

# Run the application
if __name__ == "__main__":
    # load environment variables from .env file
    load_dotenv()

    app = QApplication(sys.argv)
    app.setApplicationName("BuRD Control Program")
    app.setWindowIcon(QIcon("NestUi/Gui/GuiImages/EchoNetLogo.png"))
    app.setFont(QFont("Arial", 22))

    main_window = NestMainWindow()
    main_window.setWindowIcon(QIcon("NestUi/Gui/GuiImages/EchoNetLogo.png"))
    main_window.setMinimumSize(1280,720)
    main_window.showFullScreen()
    
    sys.exit(app.exec())
