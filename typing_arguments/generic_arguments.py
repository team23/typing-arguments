"""
Generic method to make type arguments of generic models available in the class.

Example:
-------
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

You may also use this with pydantic models:
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
"""

import functools
import types
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast
from typing import _GenericAlias as TypingGenericAlias  # pyright: ignore[reportAttributeAccessIssue]

try:
    from pydantic import BaseModel as _PydanticBaseModel  # pyright: ignore[reportAssignmentType]
except ImportError:  # pragma: no cover
    # Provide fake pydantic base model
    class _PydanticBaseModel:
        pass

GenericTrackerMixinT = TypeVar("GenericTrackerMixinT")

TYPING_ATTRIBUTE_NAME = "__typing_arguments__"


class GenericArgumentsMixin:
    if TYPE_CHECKING:  # pragma: no cover
        # Same as TYPING_ATTRIBUTE_NAME
        __typing_arguments__: dict[TypeVar, type[Any]]

    @classmethod
    @functools.lru_cache(maxsize=None, typed=True)
    def __class_getitem__(
        cls: type[GenericTrackerMixinT],
        params: type[Any] | tuple[type[Any], ...],
    ) -> type[Any]:
        if (
            cls is GenericArgumentsMixin
            and params
        ):
            raise TypeError(
                'Type parameters should be placed on typing.Generic, '
                'not GenericArgumentsMixin',
            )
        if Generic not in cls.__bases__:
            raise TypeError(
                'Cannot provide type arguments to a non-generic class, must '
                'inherit from typing.Generic first',
            )
        if not isinstance(params, tuple):
            params = (params,)

        base_cls = cls
        if issubclass(cls, _PydanticBaseModel):
            base_cls = super().__class_getitem__(params)  # pyright: ignore[reportAttributeAccessIssue]

        if len(cls.__parameters__) != len(params):  # pyright: ignore[reportAttributeAccessIssue]
            raise TypeError(
                f'Type {cls.__name__} expects {len(cls.__parameters__)} '  # pyright: ignore[reportAttributeAccessIssue]
                f'parameters, got {len(params)}',
            )

        typing_args = dict(zip(cls.__parameters__, params, strict=True))  # pyright: ignore[reportAttributeAccessIssue]
        if hasattr(cls, TYPING_ATTRIBUTE_NAME):
            typing_args = {
                **getattr(cls, TYPING_ATTRIBUTE_NAME),
                **typing_args,
            }

        typed_cls = cast(
            type[GenericArgumentsMixin],
            types.new_class(
                f"Typed{cls.__name__}",
                (base_cls,),
                {},
                lambda ns: ns.update({TYPING_ATTRIBUTE_NAME: typing_args}),
            ),
        )

        if issubclass(cls, _PydanticBaseModel):
            return typed_cls

        typed_alias = TypingGenericAlias(typed_cls, params)
        setattr(typed_alias, TYPING_ATTRIBUTE_NAME, typing_args)
        return typed_alias

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not hasattr(cls, TYPING_ATTRIBUTE_NAME):
            setattr(cls, TYPING_ATTRIBUTE_NAME, {})

        base_typing_args = {}
        typing_args = getattr(cls, TYPING_ATTRIBUTE_NAME)
        for base in reversed(cls.__bases__):
            if hasattr(base, TYPING_ATTRIBUTE_NAME):
                base_typing_args.update(getattr(base, TYPING_ATTRIBUTE_NAME))

        setattr(
            cls, TYPING_ATTRIBUTE_NAME, {
                **base_typing_args,
                **typing_args,
            },
        )


class typing_arg:
    __slots__ = ("type_argument",)

    def __init__(self, type_argument: TypeVar, /) -> None:
        self.type_argument = type_argument

    def __get__(
        self,
        obj: GenericArgumentsMixin,
        obj_class: type[GenericArgumentsMixin] | None = None,
    ) -> type[Any]:
        if obj_class is None:  # pragma: no cover
            obj_class = obj.__class__

        if not hasattr(obj_class, TYPING_ATTRIBUTE_NAME):
            raise TypeError(
                f"{obj_class} seems not be be using GenericArgumentsMixin or "
                f"no arguments were provided",
            )
        if self.type_argument not in getattr(obj_class, TYPING_ATTRIBUTE_NAME):
            raise TypeError(
                f"Type argument {self.type_argument} not found in {obj_class}",
            )

        return getattr(obj_class, TYPING_ATTRIBUTE_NAME)[self.type_argument]
