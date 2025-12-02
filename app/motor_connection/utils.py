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
