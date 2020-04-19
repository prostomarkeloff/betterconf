import os
import typing
from collections import defaultdict

from betterconf.caster import AbstractCaster
from betterconf.caster import DEFAULT_CASTER

_NO_DEFAULT = object()


class BetterconfError(Exception):
    pass


class VariableNotFoundError(BetterconfError):
    def __init__(self, variable_name: str):
        self.var_name = variable_name
        self.message = "Variable ({}) is not found".format(variable_name)
        super().__init__(self.message)


def is_callable(obj):
    """Checks that object is callable (needed for default values)"""
    return callable(obj)


class AbstractProvider:
    """Implement this class and pass to `field`"""

    def get(self, name: str) -> typing.Any:
        """Return a value or None"""
        raise NotImplementedError()


class EnvironmentProvider(AbstractProvider):
    """Default provider. Gets vals from environment"""

    def get(self, name: str) -> typing.Any:
        return os.getenv(name)


DEFAULT_PROVIDER = EnvironmentProvider()


class Field:
    def __init__(
        self,
        name: typing.Optional[str] = None,
        default: typing.Optional[typing.Any] = _NO_DEFAULT,
        provider: AbstractProvider = DEFAULT_PROVIDER,
        caster: AbstractCaster = DEFAULT_CASTER,
    ):
        """
        :param name: if you do not put down a name, then it is generated independently at the time of the request
                     for value in MetaConfig.update
        :param default:
        :param provider:
        :param caster:
        """
        self.name = name
        self._provider = provider
        self._value = None
        self._default = default
        self._caster = caster

    @property
    def value(self):
        if self.name is None:
            raise VariableNotFoundError('no name')
        self._value = self._provider.get(self.name)
        if not self._value:
            if self._default is _NO_DEFAULT:
                raise VariableNotFoundError(self.name)
            if is_callable(self._default):
                return self._default()
            else:
                return self._default
        return self._caster.cast(self._value)


class FieldInfo(typing.NamedTuple):
    name_to_set: str
    obj: Field


def field(
    name: typing.Optional[str] = None,
    default: typing.Optional[typing.Any] = _NO_DEFAULT,
    provider: AbstractProvider = DEFAULT_PROVIDER,
    caster: AbstractCaster = DEFAULT_CASTER,
) -> Field:
    return Field(name, default, provider, caster)


def is_dunder(name: str) -> bool:
    if name.startswith("__") and name.endswith("__"):
        return True
    else:
        return False


class NoValuesSet:
    """Storage of not installed configs"""
    # configs without set values
    __config_to_fields_no_value: typing.Dict[str, typing.Dict[str, Field]] = defaultdict(dict)
    # configs with set values
    __config_to_fields: typing.Dict[str, typing.Set[str]] = defaultdict(set)

    @classmethod
    def add(cls, name_config_class: str, _field: Field) -> None:
        cls.__config_to_fields_no_value[name_config_class][_field.name] = _field

    @classmethod
    def delete(cls, name_config_class: str, _field: Field) -> None:
        cls.__config_to_fields[name_config_class].add(_field.name)

    @classmethod
    def check_error(cls, name_config_class: str) -> None:
        """Throws an error if the config has undefined fields"""
        names_fields_not_values = set(cls.__config_to_fields_no_value.get(name_config_class, {}).keys())
        names_fields = cls.__config_to_fields.get(name_config_class, set())
        if names_fields_not_values - names_fields:
            raise VariableNotFoundError(
                ', '.join(names_fields_not_values - names_fields)
            )


class MetaConfig(type):
    def __new__(mcs, class_name, bases, attrs):
        new_config = super().__new__(mcs, class_name, bases, attrs)
        prefix: str = str(attrs.get('__prefix__', 'APP')).upper()
        mcs.update(class_name, prefix, new_config)
        return new_config

    @classmethod
    def update(mcs, class_name: str, path: str, sub_config):
        """
        Put the value in the configs
        :param class_name: class config name
        :param path: path to config
        :param sub_config:
        :return:
        """
        for i_name_field in dir(sub_config):
            if is_dunder(i_name_field):
                continue
            i_sub_config = getattr(sub_config, i_name_field)
            if isinstance(i_sub_config, Field):
                try:
                    if i_sub_config.name is None:
                        i_sub_config.name = f'{path}.{i_name_field}'.replace('.', '_').upper()
                    i_value = i_sub_config.value
                    NoValuesSet.delete(class_name, i_sub_config)
                except VariableNotFoundError:
                    i_value = i_sub_config
                    NoValuesSet.add(class_name, i_sub_config)
                setattr(sub_config, i_name_field, i_value)
            elif type(i_sub_config) is type:
                mcs.update(class_name, f'{path}.{i_name_field}', i_sub_config)


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


class Config(metaclass=MetaConfig):
    def __init__(self, **to_override):
        result = parse_objects(self)
        for obj in result:
            if obj.name_to_set in to_override:
                setattr(self, obj.name_to_set, to_override.get(obj.name_to_set))
                continue
            setattr(self, obj.name_to_set, obj.obj.value)

    @classmethod
    def required_fields(cls) -> None:
        NoValuesSet.check_error(cls.__name__)

    @classmethod
    def to_dict(cls, config=None) -> dict:
        result = dict()
        for i_name in dir(config or cls):
            if is_dunder(i_name):
                continue
            i_var = getattr(config or cls, i_name)
            if type(i_var) is type:
                result[i_name] = cls.to_dict(config=i_var)
                continue
            if i_name in ['required_fields', 'to_dict']:
                continue
            result[i_name] = i_var
        return result


__all__ = (
    "Config",
    "field",
    "AbstractProvider",
    "EnvironmentProvider",
    "BetterconfError",
    "VariableNotFoundError",
)
