"""
Python configs made smooth and easy.
"""

from .decorator import betterconf
from ._config import Prefix
from ._field import field, Field, constant_field, reference_field, value
from ._specials import Alias
from .provider import (
    AbstractProvider,
    JSONProvider,
    EnvironmentProvider,
    DotenvProvider,
)
from .caster import (
    to_int,
    to_bool,
    to_list,
    to_float,
    to_loguru_log_level,
    to_logging_log_level,
    AbstractCaster,
)
from .exceptions import (
    ImpossibleToCastError,
    BetterconfError,
    VariableNotFoundError,
)

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
    "EnvironmentProvider",
    "to_int",
    "to_bool",
    "to_list",
    "to_float",
    "to_loguru_log_level",
    "to_logging_log_level",
    "AbstractCaster",
    "BetterconfError",
    "VariableNotFoundError",
    "ImpossibleToCastError",
    "DotenvProvider",
    "__author__",
)
