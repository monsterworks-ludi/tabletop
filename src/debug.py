from icecream import ic  # type: ignore


IC_DEPTH = 0


def turn_on_ic():
    global IC_DEPTH
    IC_DEPTH += 1
    info = f"ic down, current depth: {IC_DEPTH}"
    ic.enable()
    ic(info)


def turn_off_ic():
    global IC_DEPTH
    IC_DEPTH -= 1
    if IC_DEPTH <= 0:
        info = f"ic disabled"
        ic(info)
        ic.disable()
    else:
        info = f"ic up, current depth: {IC_DEPTH}"
        ic(info)

def cleanup():
    return


def debug(func):
    """
    toggles ic printing for the wrapped function

    :param func: function to be wrapped
    :return: the wrapped function
    """

    def wrapper(*arg):
        ic.enable()
        print("ic enabled")
        res = func(*arg)
        ic.disable()
        print("ic disabled")
        return res

    return wrapper
