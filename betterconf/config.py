import os
import typing


class AbstractProvider:
    """Implement this class and pass to `field`"""

    def get(self, name: str) -> typing.Any:
        """Return a value or None"""
        raise NotImplementedError()


class EnvironmentProvider(AbstractProvider):
    """Default provider. Get vals from environment"""

    def get(self, name: str) -> typing.Any:
        return os.getenv(name)


DEFAULT_PROVIDER = EnvironmentProvider()


class Field:
    def __init__(
        self,
        name: str,
        default: typing.Optional[typing.Any] = None,
        provider: AbstractProvider = DEFAULT_PROVIDER,
    ):
        self._value = provider.get(name)
        self._default = default

    @property
    def value(self):
        if not self._value:
            if not self._default:
                raise ValueError("Variable is not found")
            return self._default
        return self._value


class FieldInfo(typing.NamedTuple):
    name_to_set: str
    obj: Field


def field(
    name: str,
    default: typing.Optional[typing.Any] = None,
    provider: AbstractProvider = DEFAULT_PROVIDER,
) -> Field:
    return Field(name, default, provider)


def is_dunder(name: str) -> bool:
    if name.startswith("__") and name.endswith("__"):
        return True
    else:
        return False


def parse_objects(
    obj_to_parse: typing.Union[typing.Type["Config"], "Config"]
) -> typing.List[FieldInfo]:
    result = []
    for var in dir(obj_to_parse):
        name_to_set = var
        obj = getattr(obj_to_parse, var)
        if not isinstance(obj, Field):
            continue
        if is_dunder(name_to_set):
            continue
        result.append(FieldInfo(name_to_set=name_to_set, obj=obj))
    return result


class Config:
    def __init__(self, **to_override):
        result = parse_objects(self)
        for obj in result:
            if obj.name_to_set in to_override:
                setattr(self, obj.name_to_set, to_override.get(obj.name_to_set))
                continue
            setattr(self, obj.name_to_set, obj.obj.value)


__all__ = ("Config", "field", "AbstractProvider", "EnvironmentProvider")
