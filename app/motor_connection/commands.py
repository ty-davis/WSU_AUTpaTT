#!/usr/bin/env python3
import sys
import serial
import asyncio
from asyncio import Queue
import traceback
import time
from .codes import STATUS_CODES, RESPONSE_CODES, STATUS_ALIASES, VALID_TYPES

class MotorConnection:
    def __init__(self, port='/dev/ttyACM0', baudrate: int=115200, use_scalars: bool=True, debug: bool=False):
        self.port = port
        self.baudrate = baudrate
        self.use_scalars = use_scalars
        self.print_debug = debug
        self.serial_connection = None
        self._command_queue = Queue()
        self._queue_worker_task = None
        self._response_futures = {}
        self._command_id = 0

    async def connect_async(self):
        """Establish serial connection"""
        self.serial_connection = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        self._queue_worker_task = asyncio.create_task(self._queue_worker())

    def connect(self):
        self.serial_connection = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )

    def disconnect(self):
        """Close serial connection"""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None

    async def disconnect_async(self):
        """Close serial connection and cleanup async resources"""
        # Cancel the queue worker task
        if self._queue_worker_task:
            self._queue_worker_task.cancel()
            try:
                await self._queue_worker_task
            except asyncio.CancelledError:
                pass
            self._queue_worker_task = None

        # Clear any pending futures with an exception
        for future in self._response_futures.values():
            if not future.done():
                future.set_exception(Exception("Connection closed"))
        self._response_futures.clear()

        # Close the serial connection
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None

    def toggle_scalars(self):
        """Toggle scalars"""
        self.use_scalars = not self.use_scalars
        return self.use_scalars


    async def wait_async(self, intvl=100):
        """
        Wait until MCU is ready for new command

        Parameters
        ----------
        intvl: int
            polling interval in milliseconds

        Returns
        -------
        bool
            True if successful, False if internal error occurred
        """
        while True:
            response = await self.send_command_async('READY')
            if response['status'] == 'OK':
                return True
            elif response['status'] == 'INTL_ERROR':
                return False
            await asyncio.sleep(intvl/1000)

    def wait(self, intvl=100):
        """
        Wait until MCU is ready for new command

        Parameters
        ----------
        intvl: int
            polling interval in milliseconds

        Returns
        -------
        bool
            True if successful, False if internal error occurred
        """
        while True:
            response = self.send_command('READY')
            if response['status'] == 'OK':
                return True
            elif response['status'] == 'INTL_ERROR':
                return False
            time.sleep(intvl/1000)

    def send_command(self, command: str, *params):
        com = self.build_command(command, params)
        assert type(com) == bytearray, "Command could not be built."
        if not self.serial_connection:
            raise Exception("Command could not be sent, initialize serial connection first")
        self.serial_connection.write(com)
        self.serial_connection.flush()

        # read the response
        self.serial_connection.timeout = 0.2
        data = self.serial_connection.read(256)
        response = self.parse_response(data, com[0])
        return response

    async def _queue_worker(self):
        while True:
            try:
                command_id, command, params, future = await self._command_queue.get()
                try:
                    com = self.build_command(command, params)
                    self.serial_connection.write(com)
                    self.serial_connection.flush()

                    self.serial_connection.timeout = 0.02
                    data = await asyncio.to_thread(self.serial_connection.read, 256)
                    response = self.parse_response(data, com[0])
                    future.set_result(response)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    self._command_queue.task_done()
            except asyncio.CancelledError:
                break

    async def send_command_async(self, command: str, *params):
        com = self.build_command(command, params)
        assert type(com) == bytearray, "Command could not be built."
        if not self.serial_connection:
            raise Exception("Command could not be sent, initialize serial connection first")

        self._command_id += 1
        future = asyncio.Future()
        await self._command_queue.put((self._command_id, command, params, future))
        return await future

    def build_command(self, command: str, params):
        # parse the alias if necessary
        command = STATUS_ALIASES[command] if command in STATUS_ALIASES.keys() else command
        if command not in STATUS_CODES.keys():
            raise Exception(f"Invalid command: {command}")

        status = STATUS_CODES[command]['code']
        version = 0
        payload = self.check_params(params, STATUS_CODES[command]['params'], STATUS_CODES[command]['scalar'])

        ba = bytearray([status, version]) + payload

        return ba

    def check_params(self, params, p_list, scalar_list=None):
        """
        Check if the params match the definition in p_list

        Parameters
        ----------
        params: list
            List of the parameters
        p_list: list
            List of the proper types for the parameters

        Returns
        -------
        bytearray
            bytearray object containing the proper length and bytes for the message to send to the MCU

        """
        for p in p_list:
            if p not in VALID_TYPES.keys():
                raise Exception("Bad datatype")

        if len(p_list) != len(params):
            raise Exception(f"Command expects {len(p_list)} parameters")

        if len(p_list) == 0 and len(params) == 0:
            return bytearray([0])

        if scalar_list == None or len(scalar_list) != len(p_list):
            scalar_list = [None for _ in p_list]


        bas = []
        for (arg, p, scalar) in zip(params, p_list, scalar_list):
            new_arg = round(float(arg) * scalar) if scalar and self.use_scalars else arg
            bas.append(VALID_TYPES[p]['build_val_func'](int(new_arg)))

        ba = bytearray([])
        for _bas in bas:
            ba += bytearray(_bas)
        ba = bytearray([len(ba)]) + ba

        return ba


    def parse_response(self, msg, request_status):
        """
        Parse response from the MCU and return as dict

        Parameters
        ----------
        msg: bytearray
            Message received from MCU
        request_status: int
        """
        if len(msg) == 0:
            raise Exception("No message received from server.")

        status = msg[0]

        if status not in [x['code'] for x in RESPONSE_CODES.values()]:
            raise Exception(f"UNKNOWN CODE: {hex(status)}")

        status_title = None
        for k, v in RESPONSE_CODES.items():
            if v['code'] == status:
                status_title = k
                break
        assert status_title, "Invalid response code received from MCU"

        response_content = f"[{hex(status)}] - {RESPONSE_CODES[status_title]['description']}"
        response_values = {
            'status': status_title
        }
        if status_title != "OK_PAYLOAD":
            self.debug("NO PAYLOAD:", response_content)

        if request_status not in [x['code'] for x in STATUS_CODES.values()]:
            raise Exception(f"Unknown request status. Broken request.")


        request_title = None
        for k, v in STATUS_CODES.items():
            if v['code'] == request_status:
                request_title = k
                break
        assert request_title, "Invalid status code received from MCU"

        msg_ptr = 1

        params_list = STATUS_CODES[request_title]['response_params']
        names_list = STATUS_CODES[request_title]['response_names']
        scalar_list = STATUS_CODES[request_title]['response_scalar']
        self.debug(params_list, names_list, scalar_list)

        if params_list and (scalar_list == None or len(scalar_list) != len(params_list)):
            scalar_list = [None for _ in params_list]

        self.debug("RESPONSE:", response_content)
        if params_list and names_list and scalar_list:
            for param_type, name, scalar in zip(params_list, names_list, scalar_list):
                val, ptr_diff = VALID_TYPES[param_type]['parse_val_func'](msg[msg_ptr:])
                val = val / scalar if scalar and self.use_scalars else val
                response_values[name] = val
                msg_ptr += ptr_diff
                self.debug(f"  {name}: {val}")
        return response_values

    def debug(self, *content):
        if self.print_debug:
            print(*content)

    def open_prompt(self):
        """
        Open a prompt to send commands straight to the STM32 Motor Connection

        If a serial connection has not yet been made, it will be made.
        """
        if not self.serial_connection:
            self.connect()

        def print_help():
            print("Available commands:")
            for command, com_info in STATUS_CODES.items():
                print(f" {command}  (or {com_info['alias']})")
                print(f"   accepts {len(com_info['params'])} parameter{'s' if len(com_info['params']) > 1 else ''}\n")

            print("Additional commands:")
            for command in CUSTOM_COMMANDS.keys():
                print("  " + command)

        def toggle_scalars():
            self.use_scalars = not self.use_scalars

        CUSTOM_COMMANDS = {
            'help': print_help,
            'toggle_scalars': toggle_scalars,
        }

        print("Enter commands below ('exit' to exit)")
        while True:
            try:
                user_in = input(">> ")
                if user_in == 'exit':
                    self.disconnect()
                    print("Exiting...")
                    break
                elif user_in == '':
                    continue
                elif user_in in CUSTOM_COMMANDS.keys():
                    CUSTOM_COMMANDS[user_in]()
                    continue


                args = user_in.split()
                response = self.send_command(args[0], *args[1:])
                print(response)
            except Exception as e:
                print(e)
                traceback.print_exc()



def main(argv):
    x = MotorConnection()

if __name__ == '__main__':
    main(sys.argv)
