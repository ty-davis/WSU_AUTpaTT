from abc import ABC, abstractmethod
from motor_connection import MotorConnection
from typing import List, Tuple, Dict, Callable
import asyncio

class AbstractScan(ABC):
    def __init__(self):
        self.name: str
        self.instructions: str
        self.motor_conn: MotorConnection
        self.params: Dict
        self.log: Callable
        self._cancel_event: asyncio.Event = asyncio.Event()

    @abstractmethod
    async def run_procedure(self) -> List[Tuple[float, float, float, float]]:
        pass

    def populate_state(self, motor_conn, params, log):
        self.motor_conn = motor_conn
        self.params = params
        self.log = log

    def cancel(self):
        self._cancel_event.set()

    def reset_cancel(self):
        self._cancel_event.clear()

    async def _check_cancelled(self):
        if self._cancel_event.is_set():
            raise asyncio.CancelledError("Scan cancelled by user")

    def __str__(self):
        return f"{self.name} - {self.instructions}"

class ThreeDFastScan(AbstractScan):
    def __init__(self):
        super().__init__()
        self.name = "3D Fast Scan"
        self.instructions = """Transmit Antenna polarity should be vertical. Set AUT to φ = 90 and θ = 0"""

    async def run_procedure(self):
        self.log("IS THIS WORKING?")
        results = []
        for i in range(100):
            await self._check_cancelled()
            await asyncio.sleep(0.1)
            results.append((float(i), 0., 0., 0.))
        return results

class ThetaScan(AbstractScan):
    def __init__(self):
        super().__init__()
        self.name = "2D Scan θ"
        self.instructions = """Here are the instructions"""

    async def run_procedure(self):
        return [(0., 0., 0., 0.)]

class PhiScan(AbstractScan):
    def __init__(self):
        super().__init__()
        self.name = "2D Scan φ"
        self.instructions = """Here are the instructions"""

    async def run_procedure(self):
        return [(0., 0., 0., 0.)]



all_scans = [
    ThreeDFastScan(),
    PhiScan(),
    ThetaScan(),
]
