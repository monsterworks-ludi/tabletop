from functools import wraps

from icecream import ic  # type: ignore

IC_DEPTH = 0


def debug(func):
    """
    toggles ic printing for the wrapped function

    :param func: function to be wrapped
    :return: the wrapped function
    """

    @wraps(func)
    def wrapper_func(*arg, **kwargs):
        global IC_DEPTH
        indent = IC_DEPTH*"  "
        info = f"{indent}ic depth {IC_DEPTH} -> {IC_DEPTH + 1} in <{func.__name__}>"
        IC_DEPTH += 1
        ic.enable()
        ic(info)

        res = func(*arg, **kwargs)

        IC_DEPTH -= 1
        indent = IC_DEPTH*"  "
        if IC_DEPTH <= 0:
            info = f"{indent}ic disabled in <{func.__name__}>"
            ic(info)
            ic.disable()
        else:
            info = f"{indent}ic depth {IC_DEPTH + 1} -> {IC_DEPTH} in <{func.__name__}>"
            ic(info)

        return res

    return wrapper_func

def checkup(func):
    """
    calls an object's "check()" method before and after executing the decorated method

    :param func: function to be wrapped
    :return: the wrapped function
    """

    @wraps(func)
    def wrapper_func(*arg, **kwargs):
        arg[0].check()

        res = func(*arg, **kwargs)

        arg[0].check()
        return res

    return wrapper_func

def icp(message):
    ic(message)

if __name__ == "__main__":

    @debug
    def fact(n: int) -> int:
        """Recursive factorial implementation."""
        if n == 0:
            return 1
        else:
            return n*fact(n-1)


    assert fact(3) == 6
    assert fact.__doc__ == "Recursive factorial implementation."
