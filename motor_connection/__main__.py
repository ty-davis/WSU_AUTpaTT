from .commands import MotorConnection
from .codes import *

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
    motor = MotorConnection(debug=True)
    motor.connect()

    print("Enter commands below ('exit' to exit)")
    while True:
        try:
            user_in = input(">> ")
            if user_in == 'exit':
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
