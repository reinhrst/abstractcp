import operator
import pytest
import typing as t

import abstractcp as acp

@pytest.mark.parametrize("op", [
    operator.lt,
    operator.le,
    operator.gt,
    operator.ge,
    operator.eq,
    operator.ne,
])
@pytest.mark.parametrize("direction", ["left", "right"])
def test_compare_operator(op, direction):
    class A(acp.Abstract):
        i = acp.abstract_class_property(int)
    with pytest.raises(TypeError) as e:
        if direction == "left":
            op(A.i, 1)
        else:
            assert direction == "right"
            op(1, A.i)
    e.match("Trying to use property i on A. This is an abstract property.")

def test_hash_operator():
    class A(acp.Abstract):
        i = acp.abstract_class_property(int)
    with pytest.raises(TypeError, match="unhashable type: '_AbstractClassProperty'"):
        set([A.i])

@pytest.mark.parametrize("conversion, has_custom_error", [
    (complex, False),
    (int, False),
    (float, False),
    (bytes, False),
    (bool, True),
    (str, True),
])
def test_convert(conversion, has_custom_error):
    class A(acp.Abstract):
        i = acp.abstract_class_property(int)
    if has_custom_error:
        with pytest.raises(TypeError) as e:
            conversion(A.i)
        e.match("Trying to use property i on A. This is an abstract property.")
    else:
        with pytest.raises(TypeError, match="'_AbstractClassProperty'"):
            conversion(A.i)


def test_property_read():
    class A(acp.Abstract):
        i = acp.abstract_class_property(int)
    with pytest.raises(TypeError) as e:
        A.i.real
    e.match("Trying to use property i on A. This is an abstract property.")

def test_property_write():
    class A(acp.Abstract):
        i = acp.abstract_class_property(int)
    with pytest.raises(TypeError) as e:
        A.i.real = 3
    e.match("Trying to use property i on A. This is an abstract property.")
