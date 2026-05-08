import os
import sys
import numpy as np
from OpenGL.GL import glLineWidth
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import cv2

class plot3d(object):
    def __init__(self):
        """
        Initialize 3D plot viewer with OpenGL context error handling        
        
        """
        
        self.app = None
        self.view = None

        try:
            # Try to create QApplication with proper OpenGL context
            self.app = pg.mkQApp()
            self.view = gl.GLViewWidget()
            coord = gl.GLAxisItem()
            glLineWidth(3)
            coord.setSize(3,3,3)
            self.view.addItem(coord)
        except Exception as e:
            print(f"Warning: Could not initialize OpenGL context: {e}")
            print("Running in headless mode. Visualization will be disabled.")
            self.use_display = False
            self.app = None
            self.view = None
    
    def add_points(self, points, colors):
        points_item = gl.GLScatterPlotItem(pos=points, size=2, color=colors)
        self.view.addItem(points_item)        
    
    def add_line(self, p1, p2, color=(0,1,0,1)):
        """
        p1, p2: 3D points (3)
        color: (4) array RGB
        """
        if not self.use_display or self.view is None:
            return
        try:
            lines = np.array([[p1[0], p1[1], p1[2]],
                              [p2[0], p2[1], p2[2]]])
            lines_item = gl.GLLinePlotItem(pos=lines, mode='lines',
                                           color=color, width=3, antialias=True)
            self.view.addItem(lines_item)
        except Exception as e:
            print(f"Error adding line: {e}")
    
    def show(self):
        if not self.use_display or self.view is None or self.app is None:
            print("Cannot show visualization (headless mode or OpenGL context error)")
            return
        try:
            self.view.show()
            self.app.exec()
        except Exception as e:
            print(f"Error showing visualization: {e}")

p3d = plot3d()

# sample point cloud data and colors for visualization
points = np.array([
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
], dtype=np.float32)
pc_color = np.array([
    [1.0, 0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [1.0, 1.0, 0.0, 1.0],
], dtype=np.float32)

p3d.add_points(points, pc_color)

QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    
app = QApplication(sys.argv)
    window = GLTestWidget()
    window.resize(800, 600)
    window.setWindowTitle("Qt5 Python OpenGL Test")
    window.show()
    sys.exit(app.exec_())