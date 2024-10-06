import typing
from typing import TypeVarTuple

from betterconf.caster import AbstractCaster
from betterconf.caster import DEFAULT_CASTER
from betterconf.exceptions import VariableNotFoundError, ImpossibleToCastError
from betterconf.provider import DEFAULT_PROVIDER, AbstractProvider


class Sentinel:
    @classmethod
    def is_setinel(cls, obj: typing.Any) -> bool:
        return isinstance(obj, cls)


_NO_DEFAULT = Sentinel()

T = typing.TypeVar("T")
Ts = TypeVarTuple("Ts")
SentinelOrT = typing.Union[Sentinel, T]


class _Field(typing.Generic[T]):
    # NB: fields are:
    # 1. lazy evaluated (when .value is called, I'm sure like always when initializing), fields are
    # 2. one-timers: every time the .value is called the recompute their value (that's needed for inheritance or
    # initializing this config with new params)

    def __init__(
        self,
        name: typing.Optional[str] = None,
        default: SentinelOrT[T] = _NO_DEFAULT,
        provider: typing.Optional[AbstractProvider] = None,
        caster: AbstractCaster = DEFAULT_CASTER,
        ignore_caster_error: bool = False,
    ):
        self.name = name
        self.provider = provider
        self.default = default
        self.caster = caster
        self.ignore_caster_error = ignore_caster_error

    def _get_value(self) -> T:
        try:
            if self.name is None:
                raise VariableNotFoundError("No name was given, as is a default value")

            if not self.provider:
                self.provider = DEFAULT_PROVIDER

            inner_value = self.provider.get(self.name)
        except VariableNotFoundError as e:
            if isinstance(self.default, Sentinel):
                raise e

            if callable(self.default):
                return self.default()
            else:
                return self.default
        try:
            casted = self.caster.cast(inner_value)

        except ImpossibleToCastError as e:
            if self.ignore_caster_error:
                return e.val  # type: ignore

            else:
                raise e

        else:
            return casted

    @property
    def value(self) -> T:
        return self._get_value()

    # can be used as `default=`
    def __call__(self, *_, **__: typing.Any):
        return self.value


if typing.TYPE_CHECKING:
    Field = typing.Annotated[T, ...]
else:
    Field = _Field


def value(
    name: typing.Optional[str] = None,
    default: T | typing.Any = _NO_DEFAULT,
    provider: typing.Optional[AbstractProvider] = None,
    caster: AbstractCaster = DEFAULT_CASTER,
    ignore_caster_error: bool = False,
) -> T:
    """
    Get a field and a value exactly when it's created
    """
    f = _Field[T](name, default, provider, caster, ignore_caster_error)
    return f.value


def field(
    name: typing.Optional[str] = None,
    default: T | typing.Any = _NO_DEFAULT,
    provider: typing.Optional[AbstractProvider] = None,
    caster: AbstractCaster = DEFAULT_CASTER,
    ignore_caster_error: bool = False,
) -> T:
    """
    Create a field for your config
    """
    return typing.cast(
        T, _Field[T](name, default, provider, caster, ignore_caster_error)
    )


def reference_field(*fields: *Ts, func: typing.Callable[[*Ts], T]) -> T:
    def _default() -> T:
        vars: typing.List[typing.Any] = []
        for field in fields:
            if isinstance(field, _Field):
                vars.append(field.value)  # type: ignore
            else:
                vars.append(field)

        return func(*vars)  # type: ignore

    return typing.cast(T, _Field(default=_default))


def constant_field(const: T) -> T:
    return typing.cast(T, _Field(default=const))


__all__ = ("Field", "field", "value", "reference_field", "constant_field")
