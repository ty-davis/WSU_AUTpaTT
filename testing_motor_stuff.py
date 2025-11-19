from motor_connection import MotorConnection
from datetime import datetime
import sys

reverse = False
if len(sys.argv) > 1:
    if '-r' in sys.argv:
        reverse = True

motor_conn = MotorConnection(
    port='/dev/ttyACM0',
    baudrate=115200,
    use_scalars=True,
    debug=True,
)
motor_conn.connect()

motor_conn.send_command("MOVE_AZM_BY", 360 if not reverse else -360)
motor_conn.wait(10)
print(f"{datetime.now()}: DONE MOVING")
