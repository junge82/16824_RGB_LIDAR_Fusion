from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtOpenGL import QGLWidget

import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU        # OpenGL Utility Library, extends OpenGL functionality

import sys                    # we'll need this later to run our Qt application

class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)

    def initializeGL(self):
        """Initialize OpenGL settings"""
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        GLU.gluPerspective(45.0, 1.0, 0.1, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def resizeGL(self, w, h):
        """Handle window resize"""
        gl.glViewport(0, 0, w, h)

    def paintGL(self):
        """Render the scene"""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslatef(0.0, 0.0, -5.0)
        
        # Draw a line
        gl.glColor3f(1.0, 0.0, 0.0)  # Red color
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3f(-1.0, 0.0, 0.0)
        gl.glVertex3f(1.0, 0.0, 0.0)
        gl.glEnd()
        
        # Draw another line (Y axis)
        gl.glColor3f(0.0, 1.0, 0.0)  # Green color
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3f(0.0, -1.0, 0.0)
        gl.glVertex3f(0.0, 1.0, 0.0)
        gl.glEnd()

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)    # call the init for the parent class
        
        self.resize(500, 500)
        self.setWindowTitle('OpenGL Line Drawing')
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout()
        
        # Create and add OpenGL widget
        self.gl_widget = GLWidget()
        layout.addWidget(self.gl_widget)
        
        # Add a button to clear or update
        button = QtWidgets.QPushButton('Redraw')
        button.clicked.connect(self.gl_widget.update)
        layout.addWidget(button)
        
        central_widget.setLayout(layout)
    
    

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())