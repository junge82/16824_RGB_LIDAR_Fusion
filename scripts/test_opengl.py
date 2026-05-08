import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *

# export PYOPENGL_PLATFORM='glx'; python3 test_qt_gl.py 


class GLTestWidget(QOpenGLWidget):
    def initializeGL(self):
        """Sets up the OpenGL resources and state."""
        # Set background color to dark teal
        glClearColor(0.2, 0.3, 0.3, 1.0) 

    def resizeGL(self, w, h):
        """Sets up the OpenGL viewport whenever the widget is resized."""
        glViewport(0, 0, w, h)

    def paintGL(self):
        """Renders the OpenGL scene."""
        glClear(GL_COLOR_BUFFER_BIT)
        # Add draw calls here (e.g., glBegin/glEnd or modern VBO calls)

if __name__ == "__main__":
    # Optional: Force Desktop OpenGL if you have driver issues
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    
    app = QApplication(sys.argv)
    window = GLTestWidget()
    window.resize(800, 600)
    window.setWindowTitle("Qt5 Python OpenGL Test")
    window.show()
    sys.exit(app.exec_())