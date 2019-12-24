import os
import typing


class Field:
    def __init__(self, name: str):
        self._value = os.getenv(name)

    @property
    def value(self):
        if not self._value:
            raise ValueError("Variable is not defined!")
        return self._value


class FieldInfo(typing.NamedTuple):
    name_to_set: str
    obj: Field


def field(name: str) -> Field:
    return Field(name)


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


__all__ = (Config, field)
