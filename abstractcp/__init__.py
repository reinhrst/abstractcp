import inspect
import typing as t
from pkg_resources import get_distribution, DistributionNotFound

__project__ = __name__
print(__name__)
try:
    __version__ = get_distribution(__project__).version
except DistributionNotFound:
    VERSION = __project__ + '-' + '(local)'

class AbstractProperty:
    """
    Defines a class property as abstract
    """
    __name__: str
    __containg_klass_name__: str

    def __new__(cls):
        return object.__new__(cls)

    def __set_name__(self, containg_klass: t.Type, name: str):
        if Abstract not in containg_klass.__bases__:
            raise TypeError(
                f"Abstract class property {name} defined on non-abstract "
                f"class {containg_klass.__name__}. Make sure "
                f"{containg_klass.__name__} inherits directly from Abstract.")
        object.__setattr__(self, "__name__", name)
        object.__setattr__(
            self, "__containing_klass_name__", containg_klass.__name__)

    def raise_use(self, *args, **kwargs):
        if "__name__" not in dir(self):
            breakpoint()
        raise TypeError(
            f"Trying to use property {self.__name__} on "
            f"{self.__containing_klass_name__}. This is an abstract property.")

    def raise_use_compare(self, other) -> bool:
        # compare methods seem to need this exact interface
        self.raise_use()
        return False  # will never reach, but makes mypy happy

    def __getattr__(self, name):
        # necessary for generics (and possibly other tools)
        if name.startswith("__"):
            return super().__getattr__(name)
        self.raise_use()

    def __setattr__(self, name, value):
        # necessary for generics (and possibly other tools)
        if name.startswith("__"):
            return super().__setattr__(name, value)
        self.raise_use()

    # math
    __add__ = __sub__ = __mul__ = __matmul__ = __truediv__ = raise_use
    __floordiv__ = __mod__ = __divmod__ = __pow__ = __lshift__ = raise_use
    __rshift__ = __and__ = __xor__ = __or__ = raise_use

    # right math
    __radd__ = __rsub__ = __rmul__ = __rmatmul__ = __rtruediv__ = raise_use
    __rfloordiv__ = __rmod__ = __rdivmod__ = __rpow__ = __rlshift__ = raise_use
    __rrshift__ = __rand__ = __rxor__ = __ror__ = raise_use

    # unary
    __hash__ = raise_use
    __neg__ = __pos__ = __abs__ = __invert__ = raise_use
    __round__ = __trunc__ = __floor__ = __ceil__ = raise_use

    # compare
    __eq__ = __ne__ = __lt__ = __le__ = __gt__ = __ge__ = raise_use_compare

    # convert
    __complex__ = __int__ = __float__ = __bool__ = __bytes__ = raise_use

    # We also mask __str__, even though this may be used for debugging
    # If necessary for debugging, use repr() instead
    __str__ = raise_use

T = t.TypeVar('T')
KT = t.TypeVar('KT')
VT = t.TypeVar('VT')

if t.TYPE_CHECKING:
    AbstractInt = int
    AbstractFloat = float
    AbstractStr = str
    AbstractSequence = t.Sequence
    AbstractMapping = t.Mapping
    AbstractSet = t.Set
    AbstractFrozenSet = t.FrozenSet
else:
    class AbstractInt(AbstractProperty):
        __index__ = AbstractProperty.raise_use

    class AbstractFloat(AbstractProperty):
        pass

    class AbstractStr(AbstractProperty):
        __getitem__ = __setitem__ = AbstractProperty.raise_use
        __format__ = AbstractProperty.raise_use
        __iter__ = __len__ = AbstractProperty.raise_use
        __reversed__ = __contains__ = AbstractProperty.raise_use

    # inherit from the generic type, so that generics can be used,
    # e.g. AbstractSequence[int]
    class AbstractSequence(t.Generic[T], AbstractProperty):
        __getitem__ = __setitem__ = AbstractProperty.raise_use
        __iter__ = __len__ = AbstractProperty.raise_use
        __reversed__ = __contains__ = AbstractProperty.raise_use

    class AbstractMapping(t.Generic[KT, VT], AbstractProperty):
        __getitem__ = __setitem__ = AbstractProperty.raise_use
        __iter__ = __len__ = AbstractProperty.raise_use
        __reversed__ = __contains__ = AbstractProperty.raise_use

    class AbstractSet(t.Generic[T], AbstractProperty):
        __getitem__ = __setitem__ = AbstractProperty.raise_use
        __iter__ = __len__ = AbstractProperty.raise_use
        __reversed__ = __contains__ = AbstractProperty.raise_use

    class AbstractFrozenSet(t.Generic[T], AbstractProperty):
        __getitem__ = __setitem__ = AbstractProperty.raise_use
        __iter__ = __len__ = AbstractProperty.raise_use
        __reversed__ = __contains__ = AbstractProperty.raise_use

class Abstract:
    """
    Only direct inheritance from this class makes subclasses abstract.

    Use:
    class A(Abstract):
        x: int = Abstract.ClassProperty()
        y: int = Abstract.ClassProperty()

    class B(A):
        x: Final = 1
        y: Final = 2
    """
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if Abstract not in cls.__bases__:
            # Any class that does not have Abstract as direct parent, is
            # assumed to be non-abstract, and therefore should have all
            # properties defined
            for name in dir(cls):
                if isinstance(getattr(cls, name), AbstractProperty):
                    raise TypeError(
                        f"Class {cls.__name__} must define abstract class "
                        f"property {name}, or have Abstract as direct parent.")
