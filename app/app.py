import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import QTimer
import plotting
import matplotlib.pyplot as plt
from params_manager import ParamsManager
import pprint
import time
import os
from motor_connection import MotorConnection
from serial.serialutil import SerialException
from scans import all_scans, AbstractScan
from datetime import datetime
import asyncio
import qasync


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./gui/window.ui", self)

        self.setWindowTitle("WSU AUTpaTTv3")

        # Create timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_position)
        self.timer.start(100)   # update every 150 ms

        # load the parameters
        self.params_man = ParamsManager()

        self.mast_steps.setText(str(self.params_man.params['mast_steps']))
        self.mast_steps.editingFinished.connect(self.update_params)

        self.arm_steps.setText(str(self.params_man.params['arm_steps']))
        self.arm_steps.editingFinished.connect(self.update_params)

        self.logfile = None

        # configure the motor connection
        self.motor_conn = None
        # self.connect_to_stm32()
        self.update_motor_connection_state()

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.poll_position)
        # self.timer.start(1000)

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

        self.start_button.clicked.connect(self.run_test)
        self.cancel_button.clicked.connect(self.cancel_test)
        self.moveAzimuthByButton.clicked.connect(lambda: self.motor_command('azm'))
        self.moveElevationByButton.clicked.connect(lambda: self.motor_command('elv'))
        self.moveAzimuthToButton.clicked.connect(lambda: self.motor_command('azm_to'))
        self.moveElevationToButton.clicked.connect(lambda: self.motor_command('elv_to'))
        self.calibrateButton.clicked.connect(lambda: self.motor_command('calibrate'))
        self.lockUnlockButton.clicked.connect(lambda: self.motor_command('toggle_lock'))

        self.connect_to_stm32_button.clicked.connect(self.connect_to_stm32)
        self.disconnect_from_stm32_button.clicked.connect(self.disconnect_from_stm32)

        self.cancel_button.hide()

        for scan in all_scans:
            self.select_scan.addItem(scan.name, scan)

    def update_params(self):
        try:
            self.params_man.params["mast_steps"] = int(self.mast_steps.text())
        except ValueError:
            self.mast_steps.setText(str(self.params_man.params["mast_steps"]))

        try:
            self.params_man.params["arm_steps"] = int(self.arm_steps.text())
        except ValueError:
            self.arm_steps.setText(str(self.params_man.params["arm_steps"]))

    @qasync.asyncSlot()
    async def poll_position(self):
        if not self.motor_conn or not self.motor_conn.serial_connection:
            return
        result = await self.motor_conn.send_command_async("GET_STATE")
        azm = int(result['azm']) / 8
        azm_degrees = azm * 10000 / self.params_man.params['azm_pulse_rev'] * 360 / self.params_man.params['azm_tooth_ratio'] / 10
        elv = int(result['elv']) / 8
        elv_degrees = elv * 10000 / self.params_man.params['elv_pulse_rev'] * 360 / self.params_man.params['elv_tooth_ratio'] / 10
        locked = bool(result['locked'])
        self.azimuthLocation.display(round(azm_degrees))
        self.elevationLocation.display(round(elv_degrees))
        if locked:
            self.lockUnlockButton.setText('Unlock Motors')
        else:
            self.lockUnlockButton.setText('Lock Motors')

    def edit_parameters(self):
        ...

    @qasync.asyncSlot()
    async def motor_command(self, dir):
        if self.motor_conn and self.motor_conn.serial_connection:
            try:
                if dir == 'azm':
                    if self.moveAzimuthByValue.text():
                        amount = int(self.moveAzimuthByValue.text())
                        await self.motor_conn.send_command_async("ma", amount)
                elif dir == 'elv':
                    if self.moveElevationByValue.text():
                        amount = int(self.moveElevationByValue.text())
                        await self.motor_conn.send_command_async("me", amount)
                elif dir == 'azm_to':
                    if self.moveAzimuthToValue.text():
                        amount = int(self.moveAzimuthToValue.text())
                        await self.motor_conn.send_command_async("mat", amount)
                elif dir == 'elv_to':
                    if self.moveElevationToValue.text():
                        amount = int(self.moveElevationToValue.text())
                        await self.motor_conn.send_command_async("met", amount)
                elif dir == 'calibrate':
                    await self.motor_conn.send_command_async("c")
                elif dir == 'toggle_lock':
                    await self.motor_conn.send_command_async("tl")
            except SerialException as e:
                self.log(f"Motor communication error: {e}")
                self.update_motor_connection_state()
        else:
            print("error connecting to motors")

    def update_motor_connection_state(self):
        is_connected = bool(self.motor_conn is not None and self.motor_conn.serial_connection)

        # enable/disable buttons according to the connection state
        self.start_button.setEnabled(is_connected)
        self.moveAzimuthByButton.setEnabled(is_connected)
        self.moveElevationByButton.setEnabled(is_connected)
        self.moveAzimuthToButton.setEnabled(is_connected)
        self.moveElevationToButton.setEnabled(is_connected)
        self.calibrateButton.setEnabled(is_connected)
        self.lockUnlockButton.setEnabled(is_connected)
        self.move_with_arrows_button.setEnabled(is_connected)
        if is_connected:
            self.connect_to_stm32_button.hide()
            self.disconnect_from_stm32_button.show()
        else:
            self.connect_to_stm32_button.show()
            self.disconnect_from_stm32_button.hide()

    def log(self, *args):
        self.status_label.setText(' '.join([str(arg) for arg in args]))
        print(datetime.now(), *args)

    @qasync.asyncSlot()
    async def run_test(self):
        scan: AbstractScan = self.select_scan.currentData()
        scan.reset_cancel()
        self.progress_bar.setValue(0)

        scan.populate_state(self.motor_conn,
                            self.params_man.params,
                            self.log,
                            self.progress_bar)
        self.open_datafile()

        results = None
        try:
            self.start_button.hide()
            self.cancel_button.show()
            self.log("Starting scan...")

            results = await scan.run_procedure()
            # toggle start/cancel button and disable a bunch of stuff

            if self.datafile:
                self.log(f"Writing test results to file: {self.datafile.name}")
                plotting.write_csv_file(self.datafile, results)
            else:
                self.log(f"NO DATAFILE TO WRITE TO")
            self.plot_data(results)
        except asyncio.CancelledError:
            self.log("Scan cancelled by user")
        finally:
            self.cancel_button.hide()
            self.start_button.show()
            self.close_datafile()

        return results

    def cancel_test(self):
        scan = self.select_scan.currentData()
        scan.cancel()

        self.cancel_button.hide()
        self.start_button.show()

    @qasync.asyncSlot()
    async def connect_to_stm32(self):
        self.motor_conn = MotorConnection(
            port=self.params_man.params['usb_port'],
            baudrate=self.params_man.params['baudrate'],
            use_scalars=self.params_man.params['stm32_use_scalars'],
            debug=self.params_man.params['debug_stm32'],
        )
        try:
            await self.motor_conn.connect_async()
            self.update_motor_connection_state()
        except SerialException as e:
            print(f"Error connecting to stm32: {e}")

    @qasync.asyncSlot()
    async def disconnect_from_stm32(self):
        if self.motor_conn and self.motor_conn.serial_connection:
            await self.motor_conn.disconnect_async()
        if self.motor_conn:
            self.motor_conn = None
        self.update_motor_connection_state()

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
        dialog = ArrowsDialog(self, self.motor_conn)
        result = dialog.exec()

    def plot_data(self, data):
        if plotting.is_data_3d(data):
            x, y, z, tri = plotting.process_data_3d(data)

            self.tabWidget.setCurrentIndex(0)
            self.clear_plot()
            self.plot_3d.axes.plot_trisurf(x, y, z, triangles=tri.triangles, cmap=plt.cm.CMRmap, linewidths=0.5, antialiased=True)
            self.plot_3d.canvas.draw()
        else:
            angles, r = plotting.process_data_2d(data)

            self.tabWidget.setCurrentIndex(1)
            self.clear_plot()
            self.plot_2d.axes.plot(angles, r)
            self.plot_2d.canvas.draw()

    def clear_plot(self):
        if self.tabWidget.currentIndex() == 0:
            self.plot_3d.axes.clear()
            self.plot_3d.canvas.draw()
        else:
            self.plot_2d.axes.clear()
            if hasattr(self.plot_2d.axes, 'set_theta_zero_location'):
                self.plot_2d.axes.set_theta_zero_location('N')
                self.plot_2d.axes.set_theta_direction(-1) # clockwise
            self.plot_2d.canvas.draw()

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
            self.plot_data(data)

    def open_datafile(self):
        filename = time.strftime("%d-%b-%Y_%H-%M-%S") + self.params_man.params["filename"]
        output_file = os.path.join(self.params_man.params['output_folder'], filename)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        datafile_fp = open(output_file, 'w')
        datafile_fp.write(self.params_man.params["notes"]+"\n")
        datafile_fp.write("% Mast Angle, Arm Angle, Background RSSI, Transmission RSSI\n")
        self.datafile = datafile_fp
        self.filePathLabel.setText(self.datafile.name)
        return datafile_fp

    def close_datafile(self):
        self.datafile.flush()
        self.datafile.close()
        self.datafile = None


class ArrowsDialog(QtWidgets.QDialog):
    def __init__(self, parent, motor_conn: MotorConnection, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        uic.loadUi("./gui/arrows_dialog.ui", self)
        self.motor_conn = motor_conn

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

        shift_up_shortcut = QShortcut(QKeySequence('Shift+Up'), self)
        shift_left_shortcut = QShortcut(QKeySequence('Shift+Left'), self)
        shift_down_shortcut = QShortcut(QKeySequence('Shift+Down'), self)
        shift_right_shortcut = QShortcut(QKeySequence('Shift+Right'), self)

        up_shortcut.activated.connect(lambda: self.dir_pressed('up', 15))
        left_shortcut.activated.connect(lambda: self.dir_pressed('left', -15))
        down_shortcut.activated.connect(lambda: self.dir_pressed('down', -15))
        right_shortcut.activated.connect(lambda: self.dir_pressed('right', 15))

        shift_up_shortcut.activated.connect(lambda: self.dir_pressed('up', 1))
        shift_left_shortcut.activated.connect(lambda: self.dir_pressed('left', -1))
        shift_down_shortcut.activated.connect(lambda: self.dir_pressed('down', -1))
        shift_right_shortcut.activated.connect(lambda: self.dir_pressed('right', 1))

    def done(self, result):
        super().done(result)

    @qasync.asyncSlot()
    async def dir_pressed(self, dir, amount):
        if dir == 'up':
            await self.motor_conn.send_command_async("MOVE_ELV_BY", amount)
        elif dir == 'left':
            await self.motor_conn.send_command_async("MOVE_AZM_BY", amount)
        elif dir == 'down':
            await self.motor_conn.send_command_async("MOVE_ELV_BY", amount)
        elif dir == 'right':
            await self.motor_conn.send_command_async("MOVE_AZM_BY", amount)

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
