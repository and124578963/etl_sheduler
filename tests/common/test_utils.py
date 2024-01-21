import pytest
from common.utils import override, singleton


@singleton
class SingletoneA:
    def __init__(self, *args, **kwargs):
        self.test = args

@singleton
class SingletoneB:
    ...

@singleton
class SingletoneC(SingletoneB):
    def __init__(self, *args, **kwargs):
        self.test = args
        self.self_test()

    def self_test(self):
        print(self.test)


def test_singleton():
    some_dict = {"test":1, "test2":2, "test3": 3}
    some_list = ("test","test""test","test","test")

    assert SingletoneA(*some_list, **some_dict) is SingletoneA()
    assert SingletoneB() is SingletoneB()
    assert SingletoneC(*some_list, **some_dict) is SingletoneC()

    with pytest.raises(TypeError):
        SingletoneB(*some_list, **some_dict)




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
