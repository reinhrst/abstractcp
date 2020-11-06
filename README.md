#AbstractCP -- Abstract Class Property

This package allows one to create classes with abstract class properties.
The initial code was inspired by [this question][1] (and accepted answer) -- in
addition to me strugling many time with the same issue in the past.
I firtst wanted to just post this as separate answer, however since it includes quite
some python magic, and I would like to include quite some tests (and possibly update
the code in the future), I made it into a package (even though I'm not a big fan of
small packages that hardly do anything).

The package is python3.6 and higher. I could consider creating a version for pre-3.6;
if you want that, please create an [issue on github][2].

## TL;DR Examples
Note: the examples use [PEP-526 type hints][3]; this is obviously optional.

All examples assume the following imports:
```
import tying as t
import abstractcp as acp
```
Note that all typing (including the `import typing as t` is optional.
In addition, for python < 3.8, the `Literal` type hint can be found in
`typing_extensions`.

```
class Parser(acp.Abstract):
    PATTERN: str = acp.AbstractStr()

    @classmethod
    def parse(cls, s):
        m = re.fullmatch(cls.PATTERN, s)
        if not m:
            raise ValueError(s)
        return cls(**m.groupdict())

class FooBarParser(Parser):
    PATTERN = r"foo\s+bar"

    def __init__(...): ...

class SpamParser(Parser):
    PATTERN = r"(spam)+eggs"

    def __init__(...): ...
```

Example with (more) type hints:
```
class Array(acp.Abstract):
    payload: np.ndarray
    DIMENSIONS: int = acp.AbstractInt()

    def __init__(self, payload):
        assert len(payload) == type(self).DIMENSIONS

class Vector(Array):
    DIMENSIONS: t.Literal[1] = 1

class Matrix(Array):
    DIMENSIONS: t.Literal[2] = 2
```
Note that in the previous example, we actually fix the value for `DIMENSIONS` using `t.Literal`.
This is allowed in mypy (however it may actually be a bug that it's allowed).
It would possibly feel more natural to use a `t.Final` here, however mypy doesn't allow this.

Note that if we forget to assign a value for DIMENSIONS, an error will occur:
```
class OtherArray(Array):
    pass

> TypeError: Class OtherArray must define abstract class property DIMENSIONS, or have Abstract as direct parent
```
In some cases, however, we might indeed intend for the `OtherArray` class to be abstract as well (because we will subclass this later). If so, make OtherArray inherit from Abstract directly to fix this:
```
class OtherArray(Array, acp.Abstract):
   ...

class OtherVector(OtherArray):
    DIMENSIONS = 1
```

The following abstract types have been defined:
```
AbstractProperty()
AbstractInt()
AbstractFloat()
AbstractStr()
AbstractSequence()
AbstractMapping()
AbstractSet()
AbstractFrozenSet()
```
The different types all inherit from `AbstractProperty()`, and are mostly useful
to make sure the typehints keep working well. For a type checker, `AbstractInt()` looks the same as `int`, and therefore there are no issues if this field is used as in int everywhere.
Some types have generics:
```
class A(acp.Abstract):
     mymap = acp.AbstractMapping[str, str]()

class B(A):
    mymap = {"spam": "eggs"}
```

In order to make custom Abstract Properties:
```
if t.TYPE_CHECKING:
    AbstractDType = np.dtype
else:
    class AbstractDType(acp.AbstractProperty):
        pass
```


## Introduction
I quite often find myself in a situation where I want to store some configuration in a class-variable, so that I can get different behaviour in different subclasses.
Quite often this starts with a top-level base class that has the methods, but without a reasonable value to use in the configuration.
In addition, I want to make sure that I don't accidentally forget to set this configuration for some child class -- exactly the behaviour that one would expect from abstract classes.
However Python doesn't have a standard way to define abstract class variables (or class constants).
The search for a solution initially led me to [this question][1] -- the accepted answer works well, as long as you accept that each subclass of the parent must be non-abstract.
In addition, it would not play nice at all with type-hinting and tools like `mypy`.

So I decided to write something myself -- it started as a small StackOverflow answer, however since I felt lots of tests and docs would be required, better make it a proper module.

## Design Considerations
I had some clear requirements in mind when writing this package:
* Pythonic syntax
* Works well with [PEP-526 style type hints][3] and static type checkers (if possible without any `# type: ignore` in either this code, and the code using this module).
* No runtime slowdowns (i.e.: all the work gets done at setup-time)
* Useful error messages -- stuff needs to be explicit, no silent failures.
* No need to define all abstract class properties directly in the first child -- so an abstract class can have abstract children.

## Installation
The package is a 100% python package. Installation is as simple as
```
pip install abstractcp
```

## Use
The system consists of 2 elements: The `Abstract` base class.
Each class that is abstract (i.e. that has abstract class properties -- this is completely independent of the ways to make a class abstract in `abc`) must inherit _directly_ from `Abstract`, meaning that `Abstract` should be a direct parent. This is done so that it's explicit which classes are abstract (and hence, we can throw an error if a class is abstract and does not inherit _directly_ from `Abstract`).

The second part of the system are the `AbstractProperty` classes.
Every abstract class property gets assigned an `AbstractProperty()` instance.
Note that this can only be done in classes that have `Abstract` as a direct parent.

The module comes with a number of additional `AbstractProperty` subclasses for specific types of abstract properties.
Note that is is mostly of use for those using type hints and static type checkers.

```
AbstractProperty()
AbstractInt()
AbstractFloat()
AbstractStr()
AbstractSequence()
AbstractMapping()
AbstractSet()
AbstractFrozenSet()
```

See the Examples section above for exact use.


[1]: https://stackoverflow.com/questions/45248243/most-pythonic-way-to-declare-an-abstract-class-property
[2]: https://github.com/reinhrst/abstractcp/issues/
[3]: https://www.python.org/dev/peps/pep-0526/
