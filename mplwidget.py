# mplwidget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class MplWidget3d(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a Matplotlib figure and a canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        # Create 3D axes
        self.axes = self.figure.add_subplot(111, projection='3d')
        self.figure.tight_layout()

        # Create a navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)


class MplWidget2d(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a Matplotlib figure and a canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        # Create 3D axes
        self.axes = self.figure.add_subplot(111, projection='polar')
        self.figure.tight_layout()
        self.axes.set_theta_zero_location("N")

        # Create a navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

