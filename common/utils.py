import inspect
import sys
from typing import TypeVar, Dict

# Штука для типизации в стиле Дженериков
T = TypeVar('T')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# в python < 3.12 нет override декоратора
def override(method):
    def overrider(self, *args):
        first_base_class = self.__class__.__bases__[0]
        if not (method.__name__ in dir(first_base_class)):
            raise Exception("Function is not overrided.")
        if len(args) > 0:
            return method(self, *args)
        else:
            return method(self)

    return overrider


def get_classes_from_module(module_name, parent_class: T) -> Dict[str, T]:
    dict_etl_classes = {}
    for name, file in inspect.getmembers(sys.modules[module_name]):
        for class_name, class_obj in inspect.getmembers(file):
            if inspect.isclass(class_obj) and class_obj.__bases__[0] == parent_class:
                dict_etl_classes[class_name] = class_obj
    return dict_etl_classes
