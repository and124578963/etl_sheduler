import pytest
from common.utils import override, Singleton


class SingletonA(metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        self.test = args


class SingletonB(metaclass=Singleton):
    ...


class SingletonC(SingletonB, metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        self.test = args
        self.self_test()

    def self_test(self):
        print(self.test)


def test_singleton():
    some_dict = {"test": 1, "test2": 2, "test3": 3}
    some_list = ("test", "test""test", "test", "test")

    assert SingletonA(*some_list, **some_dict) is SingletonA()
    with pytest.raises(TypeError):
        SingletonB(*some_list, **some_dict)
    assert SingletonB() is SingletonB()
    assert SingletonC(*some_list, **some_dict) is SingletonC()


def test_override():
    class A:
        def a(self): ...

    class B(A):
        @override
        def a(self): ...

        @override
        def b(self): ...

    B().a()
    with pytest.raises(Exception):
        B().b()
