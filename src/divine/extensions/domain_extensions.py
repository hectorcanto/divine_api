import abc
from typing import Self

from pydantic import BaseModel


class AbstractBaseModel(BaseModel, abc.ABC):
    """A pydantic BaseModel not meant for instantiation just for composition (mixins) and inheritance

    Use mostly this for metaprogramming abstract BaseModels with create_model, use it to prevent
    human errors.

    If not used, ABC BaseModels are actually instantiable, due to pydantic internal behavior.
    """

    def __new__(cls, *args, **kwargs):
        """This avoids abstract to be instantiated, but allows children instantiation"""
        if cls is abc.ABC:
            raise TypeError("AbstractClass cannot be instantiated directly")
        return super().__new__(cls)


class ExtendedBaseModel(AbstractBaseModel):
    @classmethod
    def from_attributes_without_validation(cls, orm_row) -> Self:
        return cls.model_construct(**{k: getattr(orm_row, k) for k in cls.model_fields})
