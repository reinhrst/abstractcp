import typing as t

import pytest

import abstractcp as acp

try:
    Literal = t.Literal  # type: ignore
except AttributeError:
    import typing_extensions
    Literal = typing_extensions.Literal  # type: ignore


def test_create_abstractcp():
    class A(acp.Abstract):
        i: int = acp.AbstractInt()

def test_forget_abstract_inherit():
    with pytest.raises(RuntimeError, match="Error calling __set_name__") as e:
        class A():
            i: int = acp.AbstractInt()
    exc: Exception = e._excinfo[1]
    cause: Exception = exc.__cause__
    assert isinstance(cause, TypeError)
    assert str(cause) == (
        "Abstract class property i defined on non-abstract class A. "
        "Make sure A inherits directly from Abstract.")

def test_subclass_also_abstract():
    class A(acp.Abstract):
        i: int = acp.AbstractInt()

    class B(A, acp.Abstract):
        pass

def test_subclass_not_abstract():
    class A(acp.Abstract):
        i: int = acp.AbstractInt()

    class B(A):
        i: Literal[3] = 3

def test_subclass_also_abstract_no_direct_descendant():
    class A(acp.Abstract):
        i: int = acp.AbstractInt()

    with pytest.raises(TypeError, match=(
            "Class B must define abstract class property i, "
            "or have Abstract as direct parent")):
        class B(A):
            pass

def test_multi_level_subclass():
    class A(acp.Abstract):
        a: int = acp.AbstractInt()

    class B(A, acp.Abstract):
        b: t.Sequence[int] = acp.AbstractSequence[int]()

    class C(B, acp.Abstract):
        a: Literal[3] = 3
        c: str = acp.AbstractStr()

    class D(C):
        b = (1, 2, 3)
        c: Literal["spam"] = "spam"

    assert isinstance(A.a, acp.AbstractProperty)
    with pytest.raises(TypeError):
        assert A.a == 3
    assert C.a == 3
    assert D.a == 3
    assert D.b == (1, 2, 3)
    assert D.c == "spam"
