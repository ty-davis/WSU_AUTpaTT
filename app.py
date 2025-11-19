import sys
from matplotlib.tri import Triangulation
from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QShortcut, QKeySequence
import plotting
import matplotlib.pyplot as plt
from params_manager import ParamsManager

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./gui/window.ui", self)

        # load the parameters
        params_man = ParamsManager()

        # actions
        self.actionOpen_scan.triggered.connect(self.open_scan_file)
        self.actionMove_with_Arrow_Keys.triggered.connect(self.move_with_arrow_keys)
        self.actionEdit_parameters.triggered.connect(self.edit_parameters)

        # buttons
        self.clear_plot_b.clicked.connect(self.clear_plot)
        self.move_with_arrows_button.clicked.connect(self.actionMove_with_Arrow_Keys.trigger)

    def edit_parameters(self):
        ...

    def move_with_arrow_keys(self):
        dialog = ArrowsDialog(self)

        result = dialog.exec()

    def clear_plot(self):
        self.matplotlib_widget.axes.clear()
        self.matplotlib_widget.canvas.draw()

    def open_scan_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;CSV Files (*.csv)"
        )

        if file_path:
            print(f"Opening file now: {file_path}")
            data = plotting.read_csv_file(file_path)
            x, y, z, tri = plotting.process_data(data)

            self.clear_plot()
            self.matplotlib_widget.axes.plot_trisurf(x, y, z, triangles=tri.triangles, cmap=plt.cm.CMRmap, linewidths=0.5, antialiased=True)
            self.matplotlib_widget.canvas.draw()
            print("READY")

class ArrowsDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./gui/arrows_dialog.ui", self)

        up_shortcut = QShortcut(QKeySequence('Up'), self)
        left_shortcut = QShortcut(QKeySequence('Left'), self)
        down_shortcut = QShortcut(QKeySequence('Down'), self)
        right_shortcut = QShortcut(QKeySequence('Right'), self)

        up_shortcut.activated.connect(lambda: self.dir_pressed('up'))
        left_shortcut.activated.connect(lambda: self.dir_pressed('left'))
        down_shortcut.activated.connect(lambda: self.dir_pressed('down'))
        right_shortcut.activated.connect(lambda: self.dir_pressed('right'))
    
    def done(self, result):
        super().done(result)

    def dir_pressed(self, dir):
        print(f"{dir} pressed")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())
