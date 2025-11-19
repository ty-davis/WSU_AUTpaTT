# mplwidget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class MplWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a Matplotlib figure and a canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        # Create 3D axes
        self.axes = self.figure.add_subplot(111, projection='3d')

        # Create a navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

