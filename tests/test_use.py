import operator
import pytest

import abstractcp as acp

@pytest.fixture(scope="function", params=[
    acp.AbstractInt,
    acp.AbstractFloat,
    acp.AbstractStr,
    acp.AbstractSequence,
    acp.AbstractSequence[int],
    acp.AbstractMapping,
    acp.AbstractMapping[int, str],
    acp.AbstractSet,
    acp.AbstractSet[int],
    acp.AbstractFrozenSet,
    acp.AbstractFrozenSet[int],
])
def propertytype(request):
    return request.param

@pytest.fixture(scope="function", params=[
    acp.AbstractStr,
    acp.AbstractSequence,
    acp.AbstractSequence[int],
    acp.AbstractMapping,
    acp.AbstractMapping[int, str],
    acp.AbstractSet,
    acp.AbstractSet[int],
    acp.AbstractFrozenSet,
    acp.AbstractFrozenSet[int],
])
def container_propertytype(request):
    return request.param

@pytest.mark.parametrize("op", [
    operator.add,
    operator.sub,
    operator.mul,
    operator.matmul,
    operator.truediv,
    operator.floordiv,
    operator.mod,
    operator.pow,
    operator.lshift,
    operator.rshift,
    operator.and_,
    operator.xor,
    operator.or_,
    operator.lt,
    operator.le,
    operator.gt,
    operator.ge,
    operator.eq,
    operator.ne,
])
@pytest.mark.parametrize("direction", ["left", "right"])
def test_binary_operator(op, direction, propertytype):
    class A(acp.Abstract):
        i = propertytype()
    with pytest.raises(TypeError) as e:
        if direction == "left":
            op(A.i, 1)
        else:
            assert direction == "right"
            op(1, A.i)
    e.match("Trying to use property i on A. This is an abstract property.")

@pytest.mark.parametrize("op", [
    operator.neg,
    operator.pos,
    operator.abs,
    operator.invert,
])
def test_unary_operator(op, propertytype):
    class A(acp.Abstract):
        i = propertytype()
    with pytest.raises(TypeError) as e:
        op(A.i)
    e.match("Trying to use property i on A. This is an abstract property.")


def test_index_operator():
    class A(acp.Abstract):
        i: int = acp.AbstractInt()
    l = [1, 2, 3]
    with pytest.raises(TypeError) as e:
        l[A.i]
    e.match("Trying to use property i on A. This is an abstract property.")

@pytest.mark.parametrize("conv", [
    complex,
    int,
    float,
    bytes,
    bool,
    str,
])
def test_compare_operator(conv, propertytype):
    class A(acp.Abstract):
        i = propertytype()
    with pytest.raises(TypeError) as e:
        conv(A.i)
    e.match("Trying to use property i on A. This is an abstract property.")


def test_property_read(propertytype):
    class A(acp.Abstract):
        i = propertytype()
    with pytest.raises(TypeError) as e:
        A.i.real
    e.match("Trying to use property i on A. This is an abstract property.")

def test_property_write(propertytype):
    class A(acp.Abstract):
        i = propertytype()
    with pytest.raises(TypeError) as e:
        A.i.real = 3
    e.match("Trying to use property i on A. This is an abstract property.")

def setitem(x):
    x[3] = 1

@pytest.mark.parametrize("op", [
    len,
    list,
    tuple,
    dict,
    lambda x: 1 in x,
    lambda x: x[3],
    setitem,
    reversed,
])
def test_container_operator(op, container_propertytype):
    class A(acp.Abstract):
        i = container_propertytype()
    with pytest.raises(TypeError) as e:
        op(A.i)
    e.match("Trying to use property i on A. This is an abstract property.")
