import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtWidgets import QApplication, QOpenGLWidget

def main():
    # 1. Initialize the application
    # sys.argv allows the app to handle command-line arguments
    app = QApplication(sys.argv)

    # 2. Set up the UI
    window = QWidget()
    window.setWindowTitle('PyQt5 Application')
    window.setGeometry(100, 100, 400, 200) # (x, y, width, height)

    label = QLabel('Hello, Qt!', parent=window)
    label.move(160, 80)

    # 3. Show the window
    window.show()

    # 4. Run the event loop
    # sys.exit ensures a clean exit when the window is closed
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
