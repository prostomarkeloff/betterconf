import typing
import warnings

from betterconf.caster import AbstractCaster
from betterconf.caster import DEFAULT_CASTER
from betterconf.exceptions import VariableNotFoundError, ImpossibleToCastError
from betterconf.provider import DEFAULT_PROVIDER, AbstractProvider, EnvironmentProvider

_NO_DEFAULT = object()


def is_callable(obj):
    """Checks that object is callable (needed for default values)"""
    return callable(obj)


class Field:
    # NB: fields are:
    # 1. lazy evaluated (when .value is called, I'm sure like always when initializing), fields are
    # 2. one-timers: every time the .value is called the recompute their value (that's needed for inheritance or
    # initializing this config with new params)

    def __init__(
        self,
        name: typing.Optional[str] = None,
        default: typing.Optional[typing.Any] = _NO_DEFAULT,
        provider: AbstractProvider = DEFAULT_PROVIDER,
        caster: AbstractCaster = DEFAULT_CASTER,
        ignore_caster_error: bool = False,
    ):
        self.name = name
        self._provider = provider
        self._value = None
        self._default = default
        self._caster = caster
        self._ignore_caster_error = ignore_caster_error

    def _get_value(self):
        try:
            if self.name is None:
                raise VariableNotFoundError("No name")
            inner_value = self._provider.get(self.name)
        except VariableNotFoundError as e:
            if self._default is _NO_DEFAULT:
                raise e
            if is_callable(self._default):
                return self._default()
            else:
                return self._default
        try:
            casted = self._caster.cast(inner_value)

        except ImpossibleToCastError as e:
            if self._ignore_caster_error:
                return e.val

            else:
                raise e

        else:
            return casted

    @property
    def value(self):
        return self._get_value()

    # can be used as `default=`
    def __call__(self, *args, **kwargs):
        return self.value


class FieldInfo(typing.NamedTuple):
    name_to_set: str
    obj: Field


class SubConfigInfo(typing.NamedTuple):
    name_to_set: str
    obj: type


def value(
    name: typing.Optional[str] = None,
    default: typing.Optional[typing.Any] = _NO_DEFAULT,
    provider: AbstractProvider = DEFAULT_PROVIDER,
    caster: AbstractCaster = DEFAULT_CASTER,
    ignore_caster_error: bool = False,
) -> typing.Any:
    """
    Get a field and a value exactly when it's created
    """
    f = Field(name, default, provider, caster, ignore_caster_error)
    return f.value


def field(
    name: typing.Optional[str] = None,
    default: typing.Optional[typing.Any] = _NO_DEFAULT,
    provider: AbstractProvider = DEFAULT_PROVIDER,
    caster: AbstractCaster = DEFAULT_CASTER,
    ignore_caster_error: bool = False,
) -> Field:
    """
    Create a field for your config
    """
    return Field(name, default, provider, caster, ignore_caster_error)


def reference_field(*fields: Field, func: typing.Callable[..., typing.Any]) -> Field:
    return Field(default=lambda: func(*(v.value for v in fields)))

def constant_field(const: typing.Any) -> Field:
    return Field(default=const)


def compose_field(
    first_field: Field,
    second_field: Field,
    f: typing.Callable[[typing.Any, typing.Any], typing.Any],
) -> Field:
    warnings.warn(
        "The function `compose_field` is deprecated since 3.0.0\nPlease use `reference_field` due to its ability to "
        "take any count of arguments"
    )
    return reference_field(first_field, second_field, func=lambda f1, f2: f(f1, f2))


def is_dunder(name: str) -> bool:
    if name.startswith("__") and name.endswith("__"):
        return True
    else:
        return False


def as_dict(cfg: typing.Union["Config", type], exclude: typing.Optional[list[str]] = None) -> dict:
    """
    config serialization
    :param cfg:
    :param exclude:
    :return:
    """
    if not exclude:
        exclude = []

    result = dict()
    for i_name in dir(cfg):
        if i_name in exclude:
            continue
        if is_dunder(i_name):
            continue
        i_var = getattr(cfg, i_name)
        if is_callable(i_var):
            continue
        if hasattr(i_var, "__dict__"):
            result[i_name] = as_dict(i_var)
            continue
        result[i_name] = i_var
    return result


def parse_objects(
    obj_to_parse: typing.Union[typing.Type["Config"], "Config"]
) -> typing.List[typing.Union[FieldInfo, SubConfigInfo]]:
    result = []
    for var in dir(obj_to_parse):
        name_to_set = var
        if is_dunder(name_to_set):
            continue
        obj: typing.Any = getattr(obj_to_parse, var)
        if isinstance(obj, Field):
            result.append(FieldInfo(name_to_set=name_to_set, obj=obj))
        elif type(obj) is type:
            result.append(SubConfigInfo(name_to_set=name_to_set, obj=obj))
    return result


class Config:
    _prefix_: typing.Optional[str] = None
    _provider_: AbstractProvider = DEFAULT_PROVIDER

    def __init__(self, _provider_: typing.Optional[AbstractProvider] = None, **to_override):
        _provider = _provider_ or self._provider_
        self._init_fields(self._prefix_, self, _provider, **to_override)

    @classmethod
    def _init_fields(
        cls, path: str, config: typing.Union["Config", type], _provider: AbstractProvider, **to_override
    ):
        """
        Put the value in the configs
        :param path: path to config
        :param config:
        :return:
        """
        config = config() if type(config) is type else config
        path = f"{path}." if path else ""
        result = parse_objects(config)
        for obj in result:
            if obj.name_to_set in to_override:
                obj.obj._default = to_override.get(obj.name_to_set)
                setattr(config, obj.name_to_set, obj.obj.value)
                continue
            elif isinstance(obj, SubConfigInfo):
                obj: SubConfigInfo
                _path = f"{path}{obj.name_to_set}".replace(".", "_").upper()
                # if subconfig has its own default provider we use it
                # otherwise the default for master config
                sub_provider = getattr(obj.obj, "_provider_", _provider)
                sub_config = cls._init_fields(_path, obj.obj, sub_provider)
                setattr(config, obj.name_to_set, sub_config)
            else:
                if obj.obj.name is None:
                    obj.obj.name = f"{path}{obj.name_to_set}".replace(".", "_").upper()

                if obj.obj._provider is DEFAULT_PROVIDER and _provider is not DEFAULT_PROVIDER:
                    obj.obj._provider = _provider

                setattr(config, obj.name_to_set, obj.obj.value)
        return config


__all__ = (
    "Config",
    "field",
    "AbstractProvider",
    "EnvironmentProvider",
    "VariableNotFoundError",
    "reference_field",
    "compose_field",
    "value",
    "constant_field",
    "as_dict",
    "Field",  # sometimes useful for typing
)
