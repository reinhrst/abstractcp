"""
This file just contains a lot of code, to see if mypy will trip over it
"""
import typing as t

import abstractcp as acp


def require_int(i: int) -> None:
    pass

def require_str(s: str) -> None:
    pass

class A(acp.Abstract):
    i = acp.abstract_class_property(int)
    s = acp.abstract_class_property(str)
    m = acp.abstract_class_property(t.Dict[str, int])

class B(A, acp.Abstract):
    i = 3
    s = "spam"

class C(B):
    m = {"eggs": 3, "spam": 5}

require_int(A.i)
require_int(B.i)
require_int(C.i)

require_str(A.s)
require_str(B.s)
require_str(C.s)

require_int(A.m["eggs"])
require_str(list(A.m.keys())[0])

T = t.TypeVar("T", int, str)

class AA(t.Generic[T], acp.Abstract):
    VALUE_TYPE: t.Type[T] = acp.abstract_class_property(t.cast(t.Type[t.Type[T]], "union of int and str"))
    def to_value(self) -> T:
        ...
