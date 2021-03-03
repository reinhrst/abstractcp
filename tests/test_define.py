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
        i: int = acp.abstract_class_property(int)

def test_forget_abstract_inherit():
    with pytest.raises(RuntimeError, match="Error calling __set_name__") as e:
        class A():
            i: int = acp.abstract_class_property(int)
    exc: Exception = e._excinfo[1]
    cause: Exception = exc.__cause__
    assert isinstance(cause, TypeError)
    assert str(cause) == (
        "Abstract class property i defined on non-abstract class A. "
        "Make sure A inherits directly from Abstract.")

def test_subclass_also_abstract():
    class A(acp.Abstract):
        i: int = acp.abstract_class_property(int)

    class B(A, acp.Abstract):
        pass

def test_subclass_not_abstract():
    class A(acp.Abstract):
        i: int = acp.abstract_class_property(int)

    class B(A):
        i: Literal[3] = 3

def test_subclass_also_abstract_no_direct_descendant():
    class A(acp.Abstract):
        i: int = acp.abstract_class_property(int)

    with pytest.raises(TypeError, match=(
            "Class B must define abstract class property i, "
            "or have Abstract as direct parent")):
        class B(A):
            pass

def test_multi_level_subclass():
    class A(acp.Abstract):
        a: int = acp.abstract_class_property(int)

    class B(A, acp.Abstract):
        b: t.Sequence[int] = acp.abstract_class_property(t.Sequence[int])

    class C(B, acp.Abstract):
        a: Literal[3] = 3
        c: str = acp.abstract_class_property(str)

    class D(C):
        b = (1, 2, 3)
        c: Literal["spam"] = "spam"

    assert isinstance(A.a, acp._AbstractClassProperty)
    with pytest.raises(TypeError):
        assert A.a == 3
    assert C.a == 3
    assert D.a == 3
    assert D.b == (1, 2, 3)
    assert D.c == "spam"


@pytest.mark.parametrize("inherit_order", [1, -1])
def test_combine_with_abc_ABC(inherit_order):
    import abc

    class A(*((abc.ABC, acp.Abstract)[::inherit_order])):
        i: int = acp.abstract_class_property(int)

        @abc.abstractmethod
        def foo(self):
            ...

    with pytest.raises(TypeError, match=("Can't instantiate abstract class A "
                                         "with abstract method(?:s?) foo")):
        A()

    with pytest.raises(TypeError, match=("Class B must define abstract class "
                                         "property i, or have Abstract as "
                                         "direct parent.")):
        class B(A):
            def foo(self):
                pass

    class C(A):
        i = 1

        def foo(self):
            return True

    c = C()
    assert isinstance(c, A)
    assert c.i == 1
    assert c.foo()


def test_abstract_class_without_abstract_properties():
    with pytest.raises(TypeError, match="Class A is defined as abstract but does "
                       "not have any abstract class properties defined."):
        class A(acp.Abstract):
            i = 3
