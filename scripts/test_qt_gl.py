import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication
import pyqtgraph.opengl as gl
import numpy as np
import os, sys

os.environ['PYOPENGL_PLATFORM'] = 'glx'  # Force EGL backend for better compatibility
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
#pg.mkQApp()
app = QApplication(sys.argv)
v1 = gl.GLViewWidget()
v1.makeCurrent()
v1.setWindowTitle('pyqtgraph OpenGL Line Example')
v1.setGeometry(0, 0, 800, 600)


# Diagonal line example
pts = np.array([[0,0,0], [5,5,5]], dtype=np.float32)
line_aa = gl.GLLinePlotItem(pos=pts, color=(1,0,0,1), width=1, antialias=True)
v1.addItem(line_aa)
coord = gl.GLAxisItem()
v1.addItem(coord)
v1.show()


sys.exit(app.exec_())
#pg.exec()

# view = gl.GLViewWidget()
# view.show()

# # Diagonal line example
# pts = np.array([[0,0,0], [5,5,5]], dtype=np.float32)
# line_aa = gl.GLLinePlotItem(pos=pts, color=(1,0,0,1), width=1, antialias=True)
# #line_noaa = gl.GLLinePlotItem(pos=pts*1.1, color=(0,1,0,1), width=1, antialias=False)
# view.addItem(line_aa)
# #view.addItem(line_noaa)
# coord = gl.GLAxisItem()
# view.addItem(coord)
# view.doneCurrent()

# sys.exit(app.exec_())

