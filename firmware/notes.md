# Notes for the project

What does the server behavior look like?

## Protocol version 00

Wait to read bit from the client. Read 3 bytes, first
byte is status byte, second byte is protocol version,
and third byte is uint8_t for length of the message
in bytes.

Example message:
01 00 02 01 C3

01 - Status byte - Move azm motor by amount
00 - Version byte - Protocol version 0
02 - Length - 2 bytes remain in message
01 - High byte
C3 - Low byte

01C3 = 451 in decimal.

Because we are working mostly with numbers, ALL MESSAGES ARE BIG-ENDIAN


## List of all the commands/status bytes that are needed

Server response messages:
20 OK
10 OK with payload (second byte is length)
  E.g. 10 04 10 e3 20 a1
30 BUSY
40 Bad request
50 Internal error

### Movement
| Status | Client Message |  Expected Server Response |
| ------ | ------ |  ------ |
| 10     | Get position                      | 10 OK  { azm: uint16_t, elv: uint16_t }    |
| 11     | Move azm by amount                | 20 OK                                      |
| 12     | Move azm to amount                | 20 OK                                      |
| 13     | Move elv by amount                | 20 OK                                      |
| 14     | Move elv to amount                | 20 OK                                      |
| 15     | Move to azm, elv                  | 20 OK                                      |
| 20     | Get speed                         | 10 OK  { azm: uint8_t, elv: uint8_t }    |
| 21     | Set azm speed to amount           | 20 OK                                      |
| 22     | Set elv speed to amount           | 20 OK                                      |
| 23     | Set both speed to amount          | 20 OK                                      |
| 24     | Dance                             | 20 OK                                      |

### Configuration
| Status | Client Message                    | Expected Server Response      |
| ------ | ----------------              | ----------- |
| 40/41  | Set/Get azm tooth ratio           | 20 OK / 10 OK { azm: uint16_t }             |
| 42/43  | Set/Get elv tooth ratio           | 20 OK / 10 OK { elv: uint16_t }             |
| 50/51  | Set/Get azm microstep (pulse/rev) | 20 OK /                                    |
| 52/53  | Set/Get elv microstep (pulse/rev) | 20 OK                                      |

TODO: Add calibration messages

### Miscellaneous
| Status | Client Message  | Expected Server Response |
| ------ | ------ | --------------- |
| 00     | Ready?                            | 20 OK or 30 BUSY                           |

