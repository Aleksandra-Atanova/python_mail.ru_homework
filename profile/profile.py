import re
import time
import inspect
from functools import wraps


def profile(obj):
    if inspect.isfunction(obj):
        decorator = profile_func(obj)
    elif inspect.isclass(obj):
        decorator = profile_class(obj)
    else:
        raise TypeError("Can't decorate it")
    return decorator


def profile_func(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = repr(func)
        func_search = re.search(r'function (.*) ', func_name)
        if func_search:
            func_name = func_search.group(1)
        start_time = time.time()
        print('{} started'.format(func_name))
        result_func = func(*args, **kwargs)
        dt = time.time() - start_time
        print('{} finished in {:.5f}'.format(func_name, dt))
        return result_func

    return wrapper


def profile_class(klass):

    def _get_method_list():
        method_list = [_attr for _attr in dir(klass)
                       if callable(getattr(klass, _attr)) and not _attr.startswith("__") or _attr in {'__init__'}]
        return method_list

    for attr_name in _get_method_list():
        attr = getattr(klass, attr_name)
        setattr(klass, attr_name, profile_func(attr))

    return klass


if __name__ == '__main__':
    @profile
    def foo():
        time.sleep(0.1111111)

    @profile
    class Bar:
        def __init__(self):
            time.sleep(0.2222222)

    foo()
    Bar()
    print(foo)
