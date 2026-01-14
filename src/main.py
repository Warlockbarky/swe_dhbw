import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('StudyAssistant - MVP Start')
    window.setGeometry(100, 100, 400, 200)
    
    label = QLabel('StudyAssistant is initializing...', parent=window)
    label.move(100, 80)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
