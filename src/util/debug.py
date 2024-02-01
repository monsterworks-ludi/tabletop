from functools import update_wrapper

from icecream import ic  # type: ignore

IC_DEPTH = 0


# todo: this won't work with parametrized pytests
def debug(func):
    """
    toggles ic printing for the wrapped function

    :param func: function to be wrapped
    :return: the wrapped function
    """

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

    return update_wrapper(wrapper_func, func)

if __name__ == "__main__":

    @debug
    def fact(n: int) -> int:
        if n == 0:
            return 1
        else:
            return n*fact(n-1)


    fact(3)
