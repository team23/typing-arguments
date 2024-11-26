# `typing-arguments`

Typing arguments using the `Generic` base class in python are great, but they lack the ability to
easily access the type arguments at runtime. This library provides a mixin class that can be used
to make type arguments available in the class and its instances.

This is also true for classes based on `pydantic.BaseModel` for pydantic > 2.x.

## Installation

Just use `pip install typing-arguments` to install the library.

**Note:** `typing-arguments` is tested on Python `3.10`, `3.11`, `3.12` and `3.13`. This is also ensured running
all tests on all those versions using `tox`.

## Usage

### Quick Example

```python
T1 = TypeVar("T1")
T2 = TypeVar("T2", bound="SomeBaseClass")


class Something(
    GenericArgumentsMixin,
    Generic[T1, T2],
):
    t1 = typing_arg(T1)
    t2 = typing_arg(T2)


ConcreteClass = Something[str, SomeBaseClassChild]
ConcreteClass.t1  # str
ConcreteClass.t2  # SomeBaseClassChild
```

**Hint:** You may also use this with pydantic models:

```python
T1 = TypeVar("T1")
T2 = TypeVar("T2", bound="SomeBaseClass")


class SomethingModel(
    GenericArgumentsMixin,
    BaseModel,
    Generic[T1, T2],
):
    t1: ClassVar = typing_arg(T1)
    t2: ClassVar = typing_arg(T2)


ConcreteClassModel = SomethingModel[str, SomeBaseClassChild]
ConcreteClassModel.t1  # str
ConcreteClassModel.t2  # SomeBaseClassChild
```

Internally `GenericArgumentsMixin` will create a new attribute `__typing_arguments__`
inside the class and its instances. This attribute is a dictionary mapping the type
variables to their concrete types. This is useful if you want to access the type
arguments in a generic way.

The `typing_arg` function is a helper function to make the type arguments available
in the class and its instances using a nicely named attribute. This is just a
convenience function, as you can also access the type arguments directly from the
`__typing_arguments__` attribute.

**Note:** If you are using pydantic models you should use the `ClassVar` annotation
to ensure pydantic will not try to catch and validate the type arguments as normal
model fields.

You may also mix different generic base classes like so:

```python
T1 = TypeVar("T1")
T2 = TypeVar("T2", bound="SomeBaseClass")


class Base1(
    GenericArgumentsMixin,
    Generic[T1],
):
    pass


class Base2(
    GenericArgumentsMixin,
    Generic[T2],
):
    t2 = typing_arg(T2)


class Something(
    Base1[str],
    Base2[SomeBaseClassChild],
):
    t1 = typing_arg(T1)


Something.t1  # str
Something.t2  # SomeBaseClassChild
```

In this example `Base1` and `Base2` are both generic base classes. `Base1` only
defines a type argument `T1` and `Base2` only defines a type argument `T2`. The
`Something` class inherits from both `Base1` and `Base2`. Note that `Base1` does
not define a simple accessor like `t1` using `typing_arg`, while `Base2` does. This
is not a problem and can be later added by `Something` using `typing_arg` as well.

You may encounter issues using the `typing_arg` function when using type validator
like mypy or your IDE. If so you might need to use `cast` to tell the type checker
you are sure about what you are doing. For example:

```python
T1 = TypeVar("T1", bound="SomeBaseClass")


class Something(
    GenericArgumentsMixin,
    Generic[T1],
):
    t1 = cast(type[SomeBaseClass], typing_arg(T1))
```

**Note:** You will still need to use `ClassVar` when using pydantic models. This
might result in using the same type twice (inside `ClassVar` and `cast`).