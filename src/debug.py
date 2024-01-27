from icecream import ic  # type: ignore

def debug(func):
    """
    toggles ic printing for the wrapped function

    :param func: function to be wrapped
    :return: the wrapped function
    """
    def wrapper(*arg):
        ic.enable()
        res = func(*arg)
        ic.disable()
        return res

    return wrapper
