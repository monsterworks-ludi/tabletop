import sys
from contextlib import contextmanager
from importlib import import_module


@contextmanager
def ignore_site_packages_paths():
    paths = sys.path
    # remove all third-party paths
    # so that only stdlib imports will succeed
    sys.path = list(filter(
        None,
        filter(lambda i: 'site-packages' not in i, sys.path)
    ))
    yield
    sys.path = paths


def is_std_lib(module):
    if module in sys.builtin_module_names:
        return True

    with ignore_site_packages_paths():
        imported_module = sys.modules.pop(module, None)
        try:
            import_module(module)
        except ImportError:
            return False
        else:
            return True
        finally:
            if imported_module:
                sys.modules[module] = imported_module

assert is_std_lib('random')
assert is_std_lib('itertools')
assert is_std_lib('collections')
assert is_std_lib('sys')
assert is_std_lib('typing')
assert is_std_lib('functools')

assert not is_std_lib('sympy')
assert not is_std_lib('pytest')
assert not is_std_lib('icecream')
