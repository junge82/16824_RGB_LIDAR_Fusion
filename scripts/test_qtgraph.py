import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg

# 1. Global configuration to enable OpenGL hardware acceleration
pg.setConfigOptions(useOpenGL=True, antialias=True)

class PyQtGraphDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQtGraph OpenGL Demo")
        self.resize(800, 600)

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the Plot Widget
        self.plot_widget = pg.PlotWidget(title="Hardware Accelerated Real-time Plot")
        layout.addWidget(self.plot_widget)

        # Initialize Data
        self.x = np.linspace(0, 10, 500)
        self.phase = 0
        self.curve = self.plot_widget.plot(self.x, np.sin(self.x), pen='c')

        # Animation Timer
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)  # ~33 FPS

    def update(self):
        self.phase += 0.1
        data = np.sin(self.x + self.phase)
        self.curve.setData(self.x, data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyQtGraphDemo()
    window.show()
    sys.exit(app.exec_())
