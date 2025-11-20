import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import QTimer
import plotting
import matplotlib.pyplot as plt
from params_manager import ParamsManager
import pprint
from motor_connection import MotorConnection
from serial.serialutil import SerialException
from scans import all_scans, AbstractScan
from datetime import datetime
import asyncio
import qasync
import json
from pathlib import Path


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./gui/window.ui", self)

        self.setWindowTitle("WSU AUTpaTTv3")

        # Create timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_lcd)
        self.timer.start(100)   # update every 100 ms

        # load the parameters
        self.params_man = ParamsManager()

        self.logfile = None

        # configure the motor connection
        self.motor_conn = None
        self.connect_to_stm32()

        # actions
        self.actionOpen_scan.triggered.connect(self.open_scan_file)
        self.actionMove_with_Arrow_Keys.triggered.connect(self.move_with_arrow_keys)
        self.actionEdit_Parameters.triggered.connect(self.edit_parameters)
        self.actionView_Parameters.triggered.connect(self.view_parameters)
        self.actionLoad_Parameters.triggered.connect(self.load_parameters)

        # buttons
        self.clear_plot_b.clicked.connect(self.clear_plot)
        self.move_with_arrows_button.clicked.connect(self.actionMove_with_Arrow_Keys.trigger)
        self.view_params_b.clicked.connect(self.actionView_Parameters.trigger)
        self.load_params_b.clicked.connect(self.load_parameters)

        self.start_button.clicked.connect(self.start_test)
        self.cancel_button.clicked.connect(self.cancel_test)
        self.moveAzmuithByButton.clicked.connect(lambda: self.move_motor_by('azm'))
        self.moveElevationByButton.clicked.connect(lambda: self.move_motor_by('elv'))
        self.moveAzmuithToButton.clicked.connect(lambda: self.move_motor_by('azm_to'))
        self.moveElevationToButton.clicked.connect(lambda: self.move_motor_by('elv_to'))
        self.lockUnlockButton.clicked.connect(lambda: self.move_motor_by('unlock'))

        #need to make buttons for this to work talk to ty.
        #self.mast_steps.clicked.connect(lambda: self.update_params('azm_steps'))
        #self.arm_steps.clicked.connect(lambda: self.update_params('elv_steps'))
        # fix some state stuff
        self.cancel_button.hide()

        for scan in all_scans:
            self.select_scan.addItem(scan.name, scan)
    
    def update_params(self, param):
        #Open the parameters file
        PARAMS_PATH = Path("params.json")
        if not PARAMS_PATH.exists():
            raise FileNotFoundError(f"{PARAMS_PATH} not found")
        with PARAMS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Update the parameters value
        if param == 'azm_steps':
            data["mast_steps"] = int(self.mast_steps.Text())
        elif param == 'elv_steps':
            data["arm_steps"] = int(self.arm_steps.Text())
        # Write back to the file
        with PARAMS_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def update_lcd(self):
        self.motor_conn.serial_connection
        azm, elv = self.motor_conn.send_command("gp", "")
        self.ui.azmuithLocation.display(self.azm)
        self.ui.elevationLocation.display(self.elv)

    def edit_parameters(self):
        ...

    def move_motor_by(self, dir):
        ...
        if self.motor_conn.serial_connection:
            if dir == 'azm':
                amount = int(self.moveAzimuthByValue.Text())
                self.motor_conn.send_command("ma", amount)
            elif dir == 'elv':
                amount = int(self.moveElevationByValue.Text())
                self.motor_conn.send_command("me", amount)
            elif dir == 'azm_to':
                amount = int(self.moveAzmuithToValue.Text())
                self.motor_conn.send_command("mat", amount)
            elif dir == 'elv_to':
                amount = int(self.moveElevationToValue.Text())
                self.motor_conn.send_command("met", amount)
            elif dir == 'unlock':
                self.motor_conn.send_command("c", "")
        else:
            print("error connecting to motors")


    def log(self, *args):
        self.status_label.setText(' '.join(args))
        print(datetime.now(), *args)

    # def start_test_sync(self):
    #     try:
    #         loop = asyncio.get_event_loop()
    #     except RuntimeError:
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #
    #     loop.run_until_complete(self.start_test())

    @qasync.asyncSlot()
    async def start_test(self):
        scan: AbstractScan = self.select_scan.currentData()
        print("HERE")
        scan.reset_cancel()

        scan.populate_state(self.motor_conn, self.params_man.params, self.log)

        try:
            self.start_button.hide()
            self.cancel_button.show()
            self.log("Starting scan...")

            results = await scan.run_procedure()
            # toggle start/cancel button and disable a bunch of stuff

            return results
        except asyncio.CancelledError:
            self.log("Scan cancelled by user")
        finally:
            self.cancel_button.hide()
            self.start_button.show()


    def cancel_test(self):
        scan = self.select_scan.currentData()
        scan.cancel()

        self.cancel_button.hide()
        self.start_button.show()

    def connect_to_stm32(self):
        self.motor_conn = MotorConnection(
            port=self.params_man.params['usb_port'],
            baudrate=self.params_man.params['baudrate'],
            use_scalars=self.params_man.params['stm32_use_scalars'],
            debug=self.params_man.params['debug_stm32'],
        )
        try:
            self.motor_conn.connect()
        except SerialException as e:
            print(f"Error connecting to stm32: {e}")

    def load_parameters(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;CSV Files (*.csv)"
        )
        if file_path:
            self.params_man.load_params(file_path)

    def view_parameters(self):
        dialog = ViewParamsDialog(self, self.params_man.params)
        result = dialog.exec()

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
    def __init__(self, parent, motor_conn: MotorConnection, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        uic.loadUi("./gui/arrows_dialog.ui", self)

        if not motor_conn.serial_connection:
            try:
                motor_conn.connect()
            except Exception as e:
                self.label.setText(f"A connection to the STM32 could not be made: {e}")
                return

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

class ViewParamsDialog(QtWidgets.QDialog):
    def __init__(self, parent, params, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        uic.loadUi("./gui/view_params_dialog.ui", self)

        self.label.setText(pprint.pformat(params))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MyMainWindow()
    window.show()
    with loop:
        loop.run_forever()
    # sys.exit(app.exec())
