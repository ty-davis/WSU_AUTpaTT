STATUS_CODES = {
    "GET_POSITION":  {
        "code": 0x10,
        "alias": 'gp',
        "params": [],
        "scalar": None,
        "response_params": ['int16_t', 'int16_t'],
        "response_scalar": [10, 10],
        "response_names": ['azm', 'elv']
    },
    "MOVE_AZM_BY":  {
        "code": 0x11,
        "alias": 'ma',
        "params": ['int16_t'],
        "scalar": [100],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "MOVE_AZM_TO":  {
        "code": 0x12,
        "alias": 'mat',
        "params": ['int16_t'],
        "scalar": [100],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "MOVE_ELV_BY":  {
        "code": 0x13,
        "alias": 'me',
        "params": ['int16_t'],
        "scalar": [100],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "MOVE_ELV_TO":  {
        "code": 0x14,
        "alias": 'met',
        "params": ['int16_t'],
        "scalar": [100],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "MOVE_TO":  {
        "code": 0x15,
        "alias": 'mt',
        "params": ['int16_t', 'int16_t'],
        "scalar": [100, 100],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "GET_SPEED":  {
        "code": 0x20,
        "alias": 'gs',
        "params": [],
        "scalar": None,
        "response_params": ['uint16_t', 'uint16_t'],
        "response_scalar": [100, 100],
        "response_names": ['azm', 'elv']
    },
    "SET_AZM_SPEED":  {
        "code": 0x21,
        "alias": 'sas',
        "params": ['uint16_t'],
        "scalar": [100],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "SET_ELV_SPEED":  {
        "code": 0x22,
        "alias": 'ses',
        "params": ['uint16_t'],
        "scalar": [100],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "SET_SPEED":  {
        "code": 0x23,
        "alias": 'ss',
        "params": ['uint16_t', 'uint16_t'],
        "scalar": [100, 100],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "DANCE":  {
        "code": 0x24,
        "alias": 'd',
        "params": [],
        "scalar": None,
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "SET_AZM_TOOTH":  {
        "code": 0x40,
        "alias": 'sat',
        "params": ['uint16_t'],
        "scalar": [1000],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "GET_AZM_TOOTH":  {
        "code": 0x41,
        "alias": 'gat',
        "params": [],
        "scalar": None,
        "response_params": ['uint16_t'],
        "response_scalar": [1000],
        "response_names": ['azm']
    },
    "SET_ELV_TOOTH":  {
        "code": 0x42,
        "alias": 'set',
        "params": ['uint16_t'],
        "scalar": [1000],
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "GET_ELV_TOOTH":  {
        "code": 0x43,
        "alias": 'get',
        "params": [],
        "scalar": None,
        "response_params": ['uint16_t'],
        "response_scalar": [1000],
        "response_names": ['elv']
    },
    "SET_AZM_STEP":  {
        "code": 0x50,
        "alias": 'sast',
        "params": ['uint16_t'],
        "scalar": None,
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "GET_AZM_STEP":  {
        "code": 0x51,
        "alias": 'gast',
        "params": [],
        "scalar": None,
        "response_params": ['uint16_t'],
        "response_scalar": None,
        "response_names": ['azm']
    },
    "SET_ELV_STEP":  {
        "code": 0x52,
        "alias": 'sesr',
        "params": ['uint16_t'],
        "scalar": None,
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "GET_ELV_STEP":  {
        "code": 0x53,
        "alias": 'gest',
        "params": [],
        "scalar": None,
        "response_params": ['uint16_t'],
        "response_scalar": None,
        "response_names": ['elv']
    },
    "READY":  {
        "code": 0x0,
        "alias": 'r',
        "params": [],
        "scalar": None,
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
    "CALIBRATE":  {
        "code": 0x1,
        "alias": 'c',
        "params": [],
        "scalar": None,
        "response_params": None,
        "response_scalar": None,
        "response_names": None
    },
}

RESPONSE_CODES = {
    "OK_PAYLOAD": {
        "code": 0x10,
        "description": "Okay with payload",
    },
    "OK": {
        "code": 0x20,
        "description": "Okay",
    },
    "BUSY": {
        "code": 0x30,
        "description": "Busy",
    },
    "BAD_REQUEST": {
        "code": 0x40,
        "description": "Bad request",
    },
    "BAD_STEP_VAL": {
        "code": 0x41,
        "description": "Bad microstep value provided",
    },
    "INTL_ERROR": {
        "code": 0x50,
        "description": "Internal Error",
    },
}
