import sys
from .GUI import NestMainWindow
from PySide6.QtWidgets import QApplication

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("BuRD Control Program")
    main_window = NestMainWindow()
    sys.exit(app.exec())
