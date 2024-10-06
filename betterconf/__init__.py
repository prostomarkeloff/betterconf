"""Simple and very small Python library for configs. Doesn't have type-casts and other funcs, just parse env."""

from .decorator import betterconf
from ._config import Prefix
from ._field import field, Field, constant_field, reference_field, value
from ._specials import Alias
from .provider import AbstractProvider, JSONProvider

__author__ = "prostomarkeloff"
__all__ = (
    "betterconf",
    "field",
    "Field",
    "constant_field",
    "value",
    "reference_field",
    "AbstractProvider",
    "JSONProvider",
    "Alias",
    "Prefix",
    "__author__",
)
