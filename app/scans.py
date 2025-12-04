from abc import ABC, abstractmethod
from motor_connection import MotorConnection
from typing import List, Tuple, Dict, Callable
import asyncio
from serial.serialutil import SerialException
import numpy as np
import qasync
import TxRadio
import RxRadio

class AbstractScan(ABC):
    def __init__(self):
        self.name: str
        self.instructions: str
        self.motor_conn: MotorConnection
        self.params: Dict
        self.log: Callable
        self._cancel_event: asyncio.Event = asyncio.Event()
        self.progress_bar = None

    @abstractmethod
    async def run_procedure(self) -> List[Tuple[float, float, float, float]] | None:
        pass

    def populate_state(self, motor_conn, params, log, progress_bar):
        self.motor_conn = motor_conn
        self.params = params
        self.log = log
        self.progress_bar = progress_bar

    def cancel(self):
        self._cancel_event.set()

    def reset_cancel(self):
        self._cancel_event.clear()

    async def _check_cancelled(self):
        if self._cancel_event.is_set():
            raise asyncio.CancelledError("Scan cancelled by user")

    def __str__(self):
        return f"{self.name} - {self.instructions}"

class ThreeDPhiCut(AbstractScan):
    def __init__(self):
        super().__init__()
        self.name = "3D φ-cut Fast Scan"
        self.instructions = """Transmit Antenna polarity should be vertical. Set AUT to φ = 90 and θ = 0"""

    @qasync.asyncSlot()
    async def run_procedure(self):
        if not self.motor_conn.serial_connection:
            try:
                self.motor_conn.connect()
            except SerialException as e:
                self.log(f"Error connecting to the motor, scan failed: {e}")

        # initialize the radios
        radio_tx_graph = TxRadio.RadioFlowGraph(
            self.params['tx_radio_id'],
            self.params['frequency'],
            self.params['tx_freq_offset'])
        radio_rx_graph = RxRadio.RadioFlowGraph(
            self.params['rx_radio_id'],
            self.params['frequency'],
            self.params['rx_freq_offset'])

        # calculate some angles
        theta_start = self.params['arm_start_angle']
        theta_end = self.params['arm_end_angle']
        theta_steps = self.params['arm_steps']
        theta_angles = np.linspace(theta_start, theta_end, theta_steps)
        theta_step = theta_angles[1] - theta_angles[0] if len(theta_angles) > 1 else 0

        phi_steps = self.params['mast_steps']
        phi_angles = np.linspace(0, 360, phi_steps)

        self.log(f"STARTING SCAN: {self.name}")
        radio_tx_graph.start()
        await asyncio.sleep(3)

        data = np.array([])
        for i, theta in enumerate(theta_angles):
            self.progress_bar.setValue(round(i / theta_steps * 100))
            if i != 0:
                await self.motor_conn.send_command_async("MOVE_ELV_BY", theta_step)
                await self.motor_conn.wait_async(20)
            self.log("COLLECTING DATA AT θ: ", theta)
            radio_rx_graph.start()
            await self.motor_conn.send_command_async("MOVE_AZM_BY", -360 * (1 if i % 2 == 0 else -1))
            await self.motor_conn.wait_async(20)
            radio_rx_graph.stop()
            self.log("FINISHED COLLECTING AT θ: ", theta)
            antenna_data = radio_rx_graph.vector_sink_0.data()

            n = len(antenna_data)
            self.log(f"Read {n} data points")
            num_samples = phi_steps
            bin_size = n //num_samples
            avg = np.zeros(num_samples)
            for i in range(num_samples):
                avg[i] = np.sqrt(
                    np.square(antenna_data[i*bin_size:(i+1)*bin_size])
                      .sum()/bin_size
                )

            phi_angles_corrected = np.array(reversed(list(phi_angles))) if i % 2 == 0 else phi_angles
            background_rssi = np.zeros(len(avg))
            theta_row = np.array([theta for _ in phi_angles])
            cut_data = np.column_stack((phi_angles_corrected, theta_row, background_rssi, avg))
            if not data.size:
                data = cut_data.copy()
            else:
                data = np.concatenate((data, cut_data), axis=0)

            if hasattr(radio_rx_graph, 'vector_sink_0'):
                radio_rx_graph.vector_sink_0.reset()

        radio_tx_graph.stop()

        self.progress_bar.setValue(100)
        self.log("SCAN COMPLETE")
        return data

class ThreeDThetaCut(AbstractScan):
    def __init__(self):
        super().__init__()
        self.name = "3D θ-cut Fast Scan"
        self.instructions = """Transmit Antenna polarity should be vertical. Set AUT to φ = 90 and θ = 0"""

    async def run_procedure(self):
        if not self.motor_conn.serial_connection:
            try:
                self.motor_conn.connect()
            except SerialException as e:
                self.log(f"Error connecting to the motor, scan failed: {e}")

        # initialize the radios
        radio_tx_graph = TxRadio.RadioFlowGraph(
            self.params['tx_radio_id'],
            self.params['frequency'],
            self.params['tx_freq_offset'])
        radio_rx_graph = RxRadio.RadioFlowGraph(
            self.params['rx_radio_id'],
            self.params['frequency'],
            self.params['rx_freq_offset'])

        # calculate some angles
        phi_angles = []

        self.log(f"STARTING SCAN: {self.name}")
        radio_tx_graph.start()
        await asyncio.sleep(3)

        self.log("Collecting data...")
        for i, elv in enumerate(phi_angles):
            ...






        results = []
        for i in range(100):
            self.progress_bar.setValue(i)
            await self._check_cancelled()
            await asyncio.sleep(0.1)
            results.append((float(i), 0., 0., 0.))

        self.progress_bar.setValue(100)
        self.log("SCAN COMPLETE")
        return results

class ThetaScan(AbstractScan):
    def __init__(self):
        super().__init__()
        self.name = "2D Scan θ"
        self.instructions = """Set AUT to θ = 0"""

    async def run_procedure(self):
        if not self.motor_conn.serial_connection:
            try:
                self.motor_conn.connect()
            except SerialException as e:
                self.log(f"Error connecting to motor, scan failed: {e}")
                return

        # initialize the radios
        radio_tx_graph = TxRadio.RadioFlowGraph(
            self.params['tx_radio_id'],
            self.params['frequency'],
            self.params['tx_freq_offset'])
        radio_rx_graph = RxRadio.RadioFlowGraph(
            self.params['rx_radio_id'],
            self.params['frequency'],
            self.params['rx_freq_offset'])

        self.log(f"STARTING SCAN: {self.name}")
        radio_tx_graph.start()
        await asyncio.sleep(3)
        self.log("Collecting data...")
        radio_rx_graph.start()
        await self.motor_conn.send_command_async('MOVE_ELV_BY', 360)
        await self.motor_conn.wait_async(20)
        radio_rx_graph.stop()
        self.log("Collection complete")
        self.progress_bar.setValue(100)
        radio_tx_graph.stop()
        await asyncio.sleep(1)

        antenna_data = radio_rx_graph.vector_sink_0.data()
        n = len(antenna_data)
        self.log(f"Read {n} data points")
        antenna_pow = np.square(antenna_data)
        num_samples = self.params["arm_steps"]
        bin_size = n //num_samples
        avg = np.zeros(num_samples)
        for i in range(num_samples):
            avg[i] = np.sqrt(
                np.square(antenna_data[i*bin_size:(i+1)*bin_size])
                  .sum()/bin_size
            )
        theta_angles = np.linspace(0, 360, num_samples)
        phi_angles = np.zeros(len(avg))
        background_rssi = np.zeros(len(avg))
        data = np.column_stack((phi_angles, theta_angles, background_rssi, avg))

        return data

class PhiScan(AbstractScan):
    def __init__(self):
        super().__init__()
        self.name = "2D Scan φ"
        self.instructions = """Here are the instructions"""

    async def run_procedure(self):
        return [(0., 0., 0., 0.)]



all_scans = [
    ThreeDPhiCut(),
    ThreeDThetaCut(),
    PhiScan(),
    ThetaScan(),
]
