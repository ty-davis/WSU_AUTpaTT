from .commands import MotorConnection
from .codes import *
from argparse import ArgumentParser

def print_help():
    print("Available commands:")
    for command, com_info in STATUS_CODES.items():
        print(f" {command}  (or {com_info['alias']})")
        print(f"   accepts {len(com_info['params'])} parameter{'s' if len(com_info['params']) > 1 else ''}\n")

    print("Additional commands:")
    for command in CUSTOM_COMMANDS.keys():
        print("  " + command)

CUSTOM_COMMANDS = {
    'help': print_help,
    # 'toggle_scalars': toggle_scalars,
}

def main():
    parser = ArgumentParser(description="Motor connection interface")
    parser.add_argument('--usb-port', type=str, help='USB port for motor connection', default="/dev/ttyACM0")
    args = parser.parse_args()

    motor = MotorConnection(port=args.usb_port, debug=True)
    motor.connect()

    print("Enter commands below ('exit' to exit)")
    while True:
        try:
            user_in = input(">> ")
            if user_in == 'exit':
                motor.disconnect()
                print("Exiting...")
                break
            elif user_in in CUSTOM_COMMANDS.keys():
                CUSTOM_COMMANDS[user_in]()
                continue


            args = user_in.split()
            response = motor.send_command(args[0], *args[1:])
            print(response)
        except Exception as e:
            print(e)
            traceback.print_exc()

if __name__ == '__main__':
    import traceback
    main()
