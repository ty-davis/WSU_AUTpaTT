#!/usr/bin/env python3
import sys
import serial
from codes import STATUS_CODES, RESPONSE_CODES

global_state = {
    'use_scalars': True,
}


def print_help():
    print("Available commands:")
    for command, com_info in STATUS_CODES.items():
        print(f" {command}  (or {com_info['alias']})")
        print(f"   accepts {len(com_info['params'])} parameter{'s' if len(com_info['params']) > 1 else ''}\n")

    print("Additional commands:")
    for command in CUSTOM_COMMANDS.keys():
        print("  " + command)


def toggle_scalars():
    global_state['use_scalars'] = not global_state['use_scalars']
    print(f"[INFO] Scalars are {'not ' if not global_state['use_scalars'] else ''}active.")

CUSTOM_COMMANDS = {
    'help': print_help,
    'toggle_scalars': toggle_scalars,
}

def unsigned_int(val: int, m: int) -> bytearray:
    """
    Provide the bytearray for the given value and size in bits for an unsigned integer

    Parameters
    ----------
    val: int
        The value to convert to a bytearray
    m: int
        The size in bits of the bytearray

    Returns
    -------
    bytearray:
        The bytearray of val as an unsigned int of size m
    """

    # check that the interger isn't outside the bounds
    if val < 0:
        raise Exception(f"val can not be less than 0: {val}")
    elif val >= 2 ** m:
        raise Exception(f"val is too large for {m} bits: {val}")

    ba_list = []
    shift = 0
    for _ in range(m // 8):
        ba_list.insert(0, (val >> shift) & 0xFF)
        shift += 8
    return bytearray(ba_list)
    

def signed_int(val, m):
    """
    Provide the bytearray for the given value and size in bits for a signed integer

    Parameters
    ----------
    val: int
        The value to convert to a bytearray
    m: int
        The size in bits of the bytearray

    Returns
    -------
    bytearray:
        The bytearray of val as a signed int of size m
    """

    # check the bounds
    if val < -(2 ** m / 2):
        raise Exception(f"val can not be less than {-(2 ** m / 2)} for {m}-bit int: {val}")
    elif val >= 2 ** m / 2:
        raise Exception(f"val can not be greater than or equal to {2 ** m / 2} for {m}-bit int: {val}")

    new_val = (2 ** m + val) & (2**m - 1)
    return unsigned_int(new_val, m)

def parse_uint(msg, m):
    val = 0
    for i in range(m // 8):
        val |= msg[i] << ((m//8-1 - i) * 8)
    return val, m // 8

def parse_int(msg, m):
    val, ptr_diff = parse_uint(msg, m)
    if val >= 2 ** m // 2:
        val -= 2 ** m
    return val, ptr_diff


STATUS_ALIASES = {v['alias']: k for k, v in STATUS_CODES.items()}

VALID_TYPES = {
    # integers
    'uint8_t': {
        'len': 1,
        'build_val_func': lambda x: unsigned_int(x, 8),
        'parse_val_func': lambda x: parse_uint(x, 8),
    },
    'int8_t': {
        'len': 1,
        'build_val_func': lambda x: signed_int(x, 8),
        'parse_val_func': lambda x: parse_int(x, 8),
    },
    'uint16_t': {
        'len': 2,
        'build_val_func': lambda x: unsigned_int(x, 16),
        'parse_val_func': lambda x: parse_uint(x, 16),
    },
    'int16_t': {
        'len': 2,
        'build_val_func': lambda x: signed_int(x, 16),
        'parse_val_func': lambda x: parse_int(x, 16),
    },
    'uint32_t': {
        'len': 4,
        'build_val_func': lambda x: unsigned_int(x, 32),
        'parse_val_func': lambda x: parse_uint(x, 32),
    },
    'int32_t': {
        'len': 4,
        'build_val_func': lambda x: signed_int(x, 32),
        'parse_val_func': lambda x: parse_int(x, 32),
    },
    'uint64_t': {
        'len': 8,
        'build_val_func': lambda x: unsigned_int(x, 64),
        'parse_val_func': lambda x: parse_uint(x, 64),
    },
    'int64_t': {
        'len': 8,
        'build_val_func': lambda x: signed_int(x, 64),
        'parse_val_func': lambda x: parse_int(x, 64),
    },
}

def check_params(argv_params, p_list, scalar_list=None):
    """
    Check if the argv_params match the definition in p_list

    Parameters
    ----------
    argv_params: list
        List of the remaining argv_parameters

    Returns
    -------
    bytearray
        bytearray object containing the proper length and bytes for the message to send to the MCU

    """
    for p in p_list:
        if p not in VALID_TYPES.keys():
            raise Exception("Bad datatype")

    if len(p_list) != len(argv_params):
        raise Exception(f"Command expects {len(p_list)} parameters")

    if len(p_list) == 0 and len(argv_params) == 0:
        return bytearray([0])

    if scalar_list == None or len(scalar_list) != len(p_list):
        scalar_list = [None for _ in p_list]


    bas = []
    for (arg, p, scalar) in zip(argv_params, p_list, scalar_list):
        new_arg = round(float(arg) * scalar) if scalar and global_state['use_scalars'] else arg
        bas.append(VALID_TYPES[p]['build_val_func'](int(new_arg)))

    ba = bytearray([])
    for _bas in bas:
        ba += bytearray(_bas)
    ba = bytearray([len(ba)]) + ba

    return ba


def build_command(args):
    if len(args) < 1:
        print("USAGE: commands.py [COMMAND] (param1) (param2) ...")
        exit()

    command = args[0]

    command = STATUS_ALIASES[command] if command in STATUS_ALIASES.keys() else command
    if command not in STATUS_CODES.keys():
        raise Exception(f"Invalid command: {command}")

    status = STATUS_CODES[command]['code']
    version = 0
    payload = check_params(args[1:], STATUS_CODES[command]['params'], STATUS_CODES[command]['scalar'])

    ba = bytearray([status, version]) + payload

    return ba


def parse_response(msg, request_status):
    print("RESPONSE ", end="")
    if len(msg) == 0:
        print("[ERROR] No message received from server.")
        return

    status = msg[0]

    if status not in [x['code'] for x in RESPONSE_CODES.values()]:
        print(f"UNKNOWN CODE: {hex(status)}")
        return

    status_title = None
    for k, v in RESPONSE_CODES.items():
        if v['code'] == status:
            status_title = k
            break

    response_content = f"[{hex(status)}] - {RESPONSE_CODES[status_title]['description']}"
    if status_title != "OK_PAYLOAD":
        print(response_content)
        return

    if request_status not in [x['code'] for x in STATUS_CODES.values()]:
        print(f"[ERROR] Unknown request status. Broken request.")
        return


    request_title = None
    for k, v in STATUS_CODES.items():
        if v['code'] == request_status:
            request_title = k
            break

    msg_ptr = 1
    response_values = {}

    params_list = STATUS_CODES[request_title]['response_params']
    names_list = STATUS_CODES[request_title]['response_names']
    scalar_list = STATUS_CODES[request_title]['response_scalar']

    if scalar_list == None or len(scalar_list) != len(params_list):
        scalar_list = [None for _ in params_list]

    print(response_content)
    for param_type, name, scalar in zip(params_list, names_list, scalar_list):
        val, ptr_diff = VALID_TYPES[param_type]['parse_val_func'](msg[msg_ptr:])
        val = val / scalar if scalar and global_state['use_scalars'] else val
        response_values[name] = val
        msg_ptr += ptr_diff
        print(f"  {name}: {val}")


def main(argv):
    # # Open serial connection
    # ser = serial.Serial(
    #     port='/dev/ttyACM0',
    #     baudrate=115200,
    #     bytesize=serial.EIGHTBITS,
    #     parity=serial.PARITY_NONE,
    #     stopbits=serial.STOPBITS_ONE
    # )
    user_in = ""
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
            ba = build_command(args)
            print("SENDING:", ''.join(f"{x:02x}" for x in ba))

            # ser.write(ba)
            # ser.flush()

            # ser.timeout = 1
            # data = ser.read(256)
            # parse_response(data, ba[0])

        except Exception as e:
            print(e)

    # ser.close()

        



if __name__ == '__main__':
    main(sys.argv)
