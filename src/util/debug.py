from icecream import ic  # type: ignore

IC_DEPTH = 0

def debug(func):
    """
    toggles ic printing for the wrapped function

    :param func: function to be wrapped
    :return: the wrapped function
    """

    def wrapper(*arg):
        global IC_DEPTH
        IC_DEPTH += 1
        info = f"ic enabled, current depth: {IC_DEPTH}"
        ic.enable()
        ic(info)

        res = func(*arg)

        IC_DEPTH -= 1
        if IC_DEPTH <= 0:
            info = f"ic disabled"
            ic(info)
            ic.disable()
        else:
            info = f"ic not disabled, current depth: {IC_DEPTH}"
            ic(info)

        return res

    return wrapper


def undebug(func):
    """
    toggles ic printing for the wrapped function

    :param func: function to be wrapped
    :return: the wrapped function
    """

    def wrapper(*arg):
        global IC_DEPTH
        IC_DEPTH -= 1
        info = f"ic disabled"
        ic(info)
        ic.disable()

        res = func(*arg)

        IC_DEPTH += 1
        if IC_DEPTH > 0:
            info = f"ic reenabled, current depth: {IC_DEPTH}"
            ic.enable()
            ic(info)
        else:
            ...

        return res

    return wrapper
