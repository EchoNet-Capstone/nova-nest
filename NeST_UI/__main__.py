import sys
from .GUI import NestMainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("BuRD Control Program")
    main_window = NestMainWindow()
    sys.exit(app.exec())
