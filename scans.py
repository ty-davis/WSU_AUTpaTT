from abc import ABC, abstractmethod
from motor_connection import MotorConnection
from typing import List, Tuple, Dict, Callable

class AbstractScan(ABC):
    def __init__(self):
        self.name: str
        self.instructions: str
        self.motor_conn: MotorConnection
        self.params: Dict
        self.log: Callable

    @abstractmethod
    def run_procedure(self) -> List[Tuple[float, float, float, float]]:
        pass

    def populate_state(self, motor_conn, params, log):
        self.motor_conn = motor_conn
        self.params = params
        self.log = log

    def __str__(self):
        return f"{self.name} - {self.instructions}"

class ThreeDFastScan(AbstractScan):
    def __init__(self):
        self.name = "3D Fast Scan"
        self.instructions = """Transmit Antenna polarity should be vertical. Set AUT to φ = 90 and θ = 0"""

    def run_procedure(self):
        return [(0., 0., 0., 0.)]

class ThetaScan(AbstractScan):
    def __init__(self):
        self.name = "2D Scan θ"
        self.instructions = """Here are the instructions"""

    def run_procedure(self):
        return [(0., 0., 0., 0.)]

class PhiScan(AbstractScan):
    def __init__(self):
        self.name = "2D Scan φ"
        self.instructions = """Here are the instructions"""

    def run_procedure(self):
        return [(0., 0., 0., 0.)]



all_scans = [
    ThreeDFastScan(),
    PhiScan(),
    ThetaScan(),
]
