from functools import wraps
from typing import TypeVar

# Штука для типизации в стиле Дженериков
T = TypeVar('T')


def singleton(orig_cls):
    orig_init = orig_cls.__init__
    orig_new = orig_cls.__new__
    instance = None

    @wraps(orig_cls.__init__)
    def __init__(self, *args, **kwargs):
        instance = orig_init(self, *args, **kwargs)
        return instance

    @wraps(orig_cls.__new__)
    def __new__(cls, *args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = orig_new(cls)
        return instance

    orig_cls.__new__ = __new__
    orig_cls.__init__ = __init__
    return orig_cls

# в python < 3.12 нет override декоратора
def override(method):
    def overrider(self, *args):
        first_base_class =  self.__class__.__bases__[0]
        if not (method.__name__ in dir(first_base_class)):
            raise Exception("Function is not overrided.")
        if len(args) > 0:
            return method(self, *args)
        else:
            return method(self)

    return overrider
