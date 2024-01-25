from icecream import ic  # type: ignore

def debug(func):
    def wrapper(*arg):
        ic.enable()
        res = func(*arg)
        ic.disable()
        return res

    return wrapper
