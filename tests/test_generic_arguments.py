from typing import ClassVar, Generic, TypeVar

import pytest
from pydantic import BaseModel

from typing_arguments import GenericArgumentsMixin, typing_arg

T1 = TypeVar("T1")
T2 = TypeVar("T2")


class PlainGeneric(GenericArgumentsMixin, Generic[T1, T2]):
    t1 = typing_arg(T1)
    t2 = typing_arg(T2)


class PlainGenericChild(PlainGeneric[str, int]):
    pass


class PlainGenericGrandChild(PlainGenericChild):
    pass


def test_plain_generic():
    type_alias = PlainGeneric[str, int]

    assert type_alias.__typing_arguments__ == {T1: str, T2: int}
    assert type_alias.t1 is str
    assert type_alias.t2 is int
    assert type_alias().t1 is str
    assert type_alias().t2 is int


def test_plain_generic_raises_exception_if_not_typed():
    assert PlainGeneric.__typing_arguments__ == {}
    with pytest.raises(TypeError):
        PlainGeneric.t1  # noqa: B018
    with pytest.raises(TypeError):
        PlainGeneric.t2  # noqa: B018
    with pytest.raises(TypeError):
        PlainGeneric().t1  # noqa: B018
    with pytest.raises(TypeError):
        PlainGeneric().t2  # noqa: B018


def test_plain_generic_raises_exception_if_base_class_is_not_generic():
    class NotGeneric(GenericArgumentsMixin):
        pass

    with pytest.raises(TypeError):
        NotGeneric[str, int]


def test_plain_generic_raises_exception_if_you_try_to_pass_typevars_to_mixin():
    with pytest.raises(TypeError):
        class TypeVarsPassedToMixin(
            GenericArgumentsMixin[T1, T2],
            Generic[T1, T2],
        ):
            pass


def test_plain_generic_raises_exception_if_you_miss_generic_base_class():
    class GenericWithoutBase(
        GenericArgumentsMixin,
    ):
        pass

    with pytest.raises(TypeError):
        GenericWithoutBase[str, int]


def test_plain_generic_raises_exception_if_wrong_arguments_count():
    with pytest.raises(TypeError):
        PlainGeneric[str]
    with pytest.raises(TypeError):
        PlainGeneric[str, int, str]


def test_plain_generic_raises_exception_if_using_typing_arg_on_non_mixin_class():
    class Something(Generic[T1]):
        t1 = typing_arg(T1)

    with pytest.raises(TypeError):
        Something[str].t1  # noqa: B018


def test_plain_generic_child():
    assert PlainGenericChild.__typing_arguments__ == {T1: str, T2: int}
    assert PlainGenericChild.t1 is str
    assert PlainGenericChild.t2 is int
    assert PlainGenericChild().t1 is str
    assert PlainGenericChild().t2 is int


def test_plain_generic__grand_child():
    assert PlainGenericGrandChild.__typing_arguments__ == {T1: str, T2: int}
    assert PlainGenericGrandChild.t1 is str
    assert PlainGenericGrandChild.t2 is int
    assert PlainGenericGrandChild().t1 is str
    assert PlainGenericGrandChild().t2 is int


class PydanticModel(GenericArgumentsMixin, BaseModel, Generic[T1, T2]):
    t1: ClassVar = typing_arg(T1)
    t2: ClassVar = typing_arg(T2)


class PydanticModelChild(PydanticModel[str, int]):
    pass


def test_pydantic_model():
    type_alias = PydanticModel[str, int]

    assert type_alias.__typing_arguments__ == {T1: str, T2: int}
    assert type_alias.t1 is str
    assert type_alias.t2 is int
    assert type_alias().t1 is str
    assert type_alias().t2 is int


def test_pydantic_model_child():
    assert PydanticModelChild.__typing_arguments__ == {T1: str, T2: int}
    assert PydanticModelChild.t1 is str
    assert PydanticModelChild.t2 is int
    assert PydanticModelChild().t1 is str
    assert PydanticModelChild().t2 is int


class Base1(GenericArgumentsMixin, Generic[T1]):
    t1 = typing_arg(T1)


class Base2(GenericArgumentsMixin, Generic[T2]):
    pass


class MultiBaseGeneric(Base1[str], Base2[int]):
    t2 = typing_arg(T2)


class MultiBaseGenericChild(MultiBaseGeneric):
    pass


def test_multi_base():
    assert MultiBaseGeneric.__typing_arguments__ == {T1: str, T2: int}
    assert MultiBaseGeneric.t1 is str
    assert MultiBaseGeneric.t2 is int
    assert MultiBaseGeneric().t1 is str
    assert MultiBaseGeneric().t2 is int


def test_multi_base_child():
    assert MultiBaseGenericChild.__typing_arguments__ == {T1: str, T2: int}
    assert MultiBaseGenericChild.t1 is str
    assert MultiBaseGenericChild.t2 is int
    assert MultiBaseGenericChild().t1 is str
    assert MultiBaseGenericChild().t2 is int
