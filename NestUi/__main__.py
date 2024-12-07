import sys
from .Gui import NestMainWindow
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("BuRD Control Program")
    app.setFont(QFont("Arial", 22))

    main_window = NestMainWindow()
    main_window.show()
    
    sys.exit(app.exec())
