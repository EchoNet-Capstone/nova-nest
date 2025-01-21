from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class NestBurdStatusMainWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        burd_status_layout = QVBoxLayout(self)
        
        # Add labels and separators
        for i in range(10):
            label = QLabel(f"Label {i + 1}")
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            burd_status_layout.addWidget(label)

            # Add a separator after each label (except the last one)
            if i < 9:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                burd_status_layout.addWidget(separator)