from .commands import MotorConnection
from .codes import *
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="Motor connection interface")
    parser.add_argument('--usb-port', type=str, help='USB port for motor connection', default="/dev/ttyACM0")
    args = parser.parse_args()

    motor = MotorConnection(port=args.usb_port, debug=True)
    motor.open_prompt()

if __name__ == '__main__':
    import traceback
    main()
