import inspect
import typing as t
from pkg_resources import get_distribution, DistributionNotFound

__project__ = __name__
try:
    __version__ = get_distribution(__project__).version
except DistributionNotFound:
    VERSION = __project__ + '-' + '(local)'

T = t.TypeVar('T')

class _AbstractClassProperty(t.Generic[T]):
    """
    Defines a class property as abstract
    """
    __name__: str
    __containg_klass_name__: str
    __propertytype_name__: str

    def __init__(self, propertytype: t.Type[T]):
        object.__setattr__(self, "__propertytype_name__", str(propertytype))

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
        # get these the hard way to avoid infinite recursion
        name = object.__getattribute__(self, "__name__")
        containg_klass_name = object.__getattribute__(
            self, "__containing_klass_name__")
        raise TypeError(
            f"Trying to use property {name} on "
            f"{containg_klass_name}. This is an abstract property.")

    def raise_use_compare(self, other) -> bool:
        # compare methods seem to need this exact interface
        self.raise_use()
        return False  # will never reach, but makes mypy happy

    def __repr__(self):
        return f"{type(self).__name__}({self.__propertytype_name__}) on " \
            f"{self.__containing_klass_name__}.{self.__name__}"

    def __getattr__(self, name):
        if name == "__isabstractmethod__":
            # Fix for the case that also inherits from abc.ABC
            raise AttributeError()
        self.raise_use()

    def __setattr__(self, name, value):
        self.raise_use()

    # disable hashing
    __hash__ = None  # type: ignore

    # next we override some of the default methods on an object that could
    # possibly be used accidentally (and give a non-error result):

    # compare
    __eq__ = __ne__ = __lt__ = __le__ = __gt__ = __ge__ = raise_use_compare

    # We only need to take care of __bool__ and __str__ since they give a result
    # on object()
    __bool__ = __str__ = raise_use

def abstract_class_property(propertytype: t.Type[T]) -> T:
    """
    Define an abstract class property of the given type
    """
    # Note that t.cast doesn't actually do anything at runtime
    return t.cast(T, _AbstractClassProperty(propertytype))


class Abstract:
    """
    Only direct inheritance from this class makes subclasses abstract.

    Use:
    class A(acp.Abstract):
        x: int = acp.abstract_class_property(int)
        y: str = acp.abstract_class_property(str)

    class B(A):
        x: t.Literal[1] = 1
        y: t.Literal["spam"] = "spam"
    """
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if Abstract in cls.__bases__:
            # Direct descendant. Make sure that at least one property is
            # actually abstract
            for name in dir(cls):
                if name.startswith("__") and name.endswith("__"):
                    # internal names are ignored since they may have magic attached
                    # when accessing
                    continue
                if isinstance(getattr(cls, name), _AbstractClassProperty):
                    break
            else:
                raise TypeError(
                    f"Class {cls.__name__} is defined as abstract but does not "
                    "have any abstract class properties defined.")
        else:
            # Any class that does not have Abstract as direct parent, is
            # assumed to be non-abstract, and therefore should have all
            # properties defined
            for name in dir(cls):
                if isinstance(getattr(cls, name), _AbstractClassProperty):
                    raise TypeError(
                        f"Class {cls.__name__} must define abstract class "
                        f"property {name}, or have Abstract as direct parent.")
