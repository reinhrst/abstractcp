# AbstractCP -- Abstract Class Property

![Tox tests](https://github.com/reinhrst/abstractcp/workflows/Tox%20tests/badge.svg)


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
```python
import tying as t
import abstractcp as acp
```
Note that all typing (including the `import typing as t` is optional.
In addition, for python < 3.8, the `Literal` type hint can be found in
`typing_extensions`.

```python
class Parser(acp.Abstract):
    PATTERN: str = acp.abstract_class_property(str)

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
```python
class Array(acp.Abstract):
    payload: np.ndarray
    DIMENSIONS: int = acp.abstract_class_property(int)

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
```python
class OtherArray(Array):
    pass

> TypeError: Class OtherArray must define abstract class property DIMENSIONS, or have Abstract as direct parent
```
In some cases, however, we might indeed intend for the `OtherArray` class to be abstract as well (because we will subclass this later). If so, make OtherArray inherit from Abstract directly to fix this:
```python
class OtherArray(Array, acp.Abstract):
   ...

class OtherVector(OtherArray):
    DIMENSIONS = 1
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
```bash
pip install abstractcp
```

## Use
The system consists of 2 elements: The `Abstract` base class.
Each class that is abstract (i.e. that has abstract class properties -- this is completely independent of the ways to make a class abstract in `abc`) must inherit _directly_ from `Abstract`, meaning that `Abstract` should be a direct parent. This is done so that it's explicit which classes are abstract (and hence, we can throw an error if a class is abstract and does not inherit _directly_ from `Abstract`).

The second part of the system is the `_AbstractClassProperty` class.
Every abstract class property gets assigned an `_AbstractClassProperty()` instance, through the `acp.abstract_class_property(...)` method. Note that this method has typehints to  return the exact class that you provide, so from a type checker point of view, `acp.abstract_class_property(int)` is identical to `3` (or `4`, or any other `int` instance). This means that we can be more flexible here, for instance doing `acp.abstract_class_property(t.Dict[str, int])`, however note that `acp.abstract_class_property(t.Mapping[str, int])` does not work, since mypy wants a concrete type there.

Note that `abstract_class_property()` can only be assigned in classes that have `Abstract` as direct parent.


See the Examples section above for exact use.

## Update from 0.9.1
Note that since 0.9.1 the syntax has changed a bit.
Rather than writing:
```python
class A(acp.Abstract):
   i = acp.AbstractInt()
```

you now use

```python
class A(acp.Abstract):
   i = acp.abstract_class_property(int)
```

It results in cleaner code, and also means that we don't have to make our own classes for new types.


## FAQ

### I'm getting `Argument 1 to "abstract_class_property" has incompatible type "object"; expected "Type[<nothing>]"` errors
    his happens when you try to feed something that is not actually a type to abstract_class_property, for instance `x = acp.abstract_class_property(t.Union[str, int])` (or even, more correctly, `t.Type[t.Union[str, int]]` or `t.Union[t.Type[str], t.Type[int]]`. Also `x = acp.abstract_class_property(t.Type[Employee])`  will not work (since `t.Type` does not actually make something a type; in this case use `type(Employee)` instead (which would give you an abstract property that could receive some subclass of Employee).

Note that the argument to `abstract_class_property` is only for readability and used in the `__repr__` of the `_AbstractClassProperty` class -- and for static typing. So as long as you satisfy static typing, all will be fine:

```
T = t.TypeVar("T", int, str)

class A(t.Generic[T], acp.Abstract):
    VALUE_TYPE: t.Type[T] = acp.abstract_class_property(t.cast(t.Type[t.Type[T]], "union of int and str"))
    def to_value(self) -> T:
        ...
```
Note the double `t.Type`, since acp.abstract_class_property will remove 1 t.Type.

[1]: https://stackoverflow.com/questions/45248243/most-pythonic-way-to-declare-an-abstract-class-property
[2]: https://github.com/reinhrst/abstractcp/issues/
[3]: https://www.python.org/dev/peps/pep-0526/
