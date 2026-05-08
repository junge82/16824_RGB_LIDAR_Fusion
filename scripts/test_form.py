import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, QtWidgets, QtOpenGL


class Ui_MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__()
        self.widget = glWidget()
        self.button = QtWidgets.QPushButton('Test', self)
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.widget)
        mainLayout.addWidget(self.button)
        self.setLayout(mainLayout)


class glWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(640, 480)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(-2.5, 0.5, -6.0)
        glColor3f( 1.0, 1.5, 0.0 );
        glPolygonMode(GL_FRONT, GL_FILL);
        glBegin(GL_TRIANGLES)
        glVertex3f(2.0,-1.2,0.0)
        glVertex3f(2.6,0.0,0.0)
        glVertex3f(2.9,-1.2,0.0)
        glEnd()
        glFlush()

    def initializeGL(self):
        glClearDepth(1.0)              
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()                    
        gluPerspective(45.0,1.33,0.1, 100.0) 
        glMatrixMode(GL_MODELVIEW)


if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)    
    Form = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(Form)    
    ui.show()    
    sys.exit(app.exec_())


# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import Qt
# import pyqtgraph.opengl as gl
# from OpenGL.GL import glLineWidth
# import sys
# import numpy as np
# import os
# #os.environ['PYOPENGL_PLATFORM'] = 'egl' 
# # 1. MUST be set before QApplication is created
# QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# # app = QApplication(sys.argv)
# # view = gl.GLViewWidget()

# # # 2. Add items BEFORE calling raw GL commands
# # coord = gl.GLAxisItem()
# # coord.setSize(3,3,3)


# # view.show()
# # view.makeCurrent()
# # box_corners = np.array([[1,2,3], [4,5,6], [7,8,9]], dtype=np.float32)  # (24,3) for box outline, float32
# # corners = np.array([
# # 	[0, 0, 0],
# # 	[1, 0, 0],
# # 	[1, 1, 0],
# # 	[0, 1, 0],
# # 	[0, 0, 1],
# # 	[1, 0, 1],
# # 	[1, 1, 1],
# # 	[0, 1, 1]
# # ], dtype=np.float32)

# # # Define the 12 edges of the box (each edge as a pair of points)
# # edges = [
# # 	[0, 1], [1, 2], [2, 3], [3, 0],  # bottom face
# # 	[4, 5], [5, 6], [6, 7], [7, 4],  # top face
# # 	[0, 4], [1, 5], [2, 6], [3, 7]   # vertical edges
# # ]

# # # Create (24,3) array for the box outline
# # box_corners = np.array([corners[start] for start, end in edges] + [corners[end] for start, end in edges], dtype=np.float32)
# # box_corners = box_corners.reshape(-1, 3)
# # box_item = gl.GLLinePlotItem(pos=box_corners, color=(1,0,0,1), width=3.0, mode='lines', antialias=True) 
# # view.addItem(coord)  # Item setup + paint() with active context
# # view.addItem(box_item)
# # app.exec()


# app = QApplication(sys.argv)
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