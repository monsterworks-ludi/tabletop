# from __future__ import unicode_literals, print_function
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

print(is_std_lib('random'))
print(is_std_lib('itertools'))
print(is_std_lib('collections'))
print(is_std_lib('sys'))
print(is_std_lib('typing'))
print(20*'#')
print(is_std_lib('sympy'))
print(is_std_lib('pytest'))
print(is_std_lib('icecream'))
