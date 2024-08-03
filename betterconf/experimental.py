"""
New way of defining configs:

```
@betterconf(provider=JSONProvider("config.json"))
class Man:
    name: str
    age: int
    job: str
```
"""

import typing
from betterconf import field as field_maker, Config as InternalConfig
from betterconf.provider import AbstractProvider, DEFAULT_PROVIDER
from betterconf.caster import _BUILTIN_CASTERS
from betterconf.config import Field
from betterconf.config import FieldInfo, SubConfigInfo, is_dunder


def parse_field(cls, name: str, annotation) -> FieldInfo:
    # for types like int, str, etc AND not initialized with `field`
    if annotation in _BUILTIN_CASTERS and name not in dir(cls):
        caster = _BUILTIN_CASTERS[annotation]
        return FieldInfo(name_to_set=name, obj=field_maker(name=name, caster=caster))
    # if it is `typing.Annotated`
    elif getattr(annotation, "__metadata__", None):
        origin = annotation.__origin__
        try:
            alias_name = annotation.__metadata__[0]
        except IndexError:
            raise ValueError(
                "The permitted pattern of use `typing.Annotated` is only `typing.Annotated[casting_type, alias_name]"
            )

        field = parse_field(cls, alias_name, origin)
        field.name_to_set = name
        return field

    elif (
        annotation in _BUILTIN_CASTERS
        and name in dir(cls)
        and isinstance(getattr(cls, name), Field)
    ):
        field: Field = getattr(cls, name)
        field._caster = _BUILTIN_CASTERS[annotation]
        return FieldInfo(name_to_set=name, obj=field)
    elif (
        annotation not in _BUILTIN_CASTERS
        and name in dir(cls)
        and isinstance(getattr(cls, name), Field)
    ):
        return FieldInfo(name_to_set=name, obj=getattr(cls, name))


def parse_fields(cls) -> typing.List[FieldInfo]:
    try:
        annotations = typing.get_type_hints(cls, include_extras=True)
    except TypeError:
        # i don't know why but when there is no annotations in class it throws TypeError
        annotations = {}
    fields = []
    # parse annotated fields
    for name, annotation in annotations.items():
        field = parse_field(cls, name, annotation)
        fields.append(field)

    # parse not annotated fields
    for f_name in dir(cls):
        field = getattr(cls, f_name)
        if isinstance(field, Field) and f_name not in annotations:
            fields.append(FieldInfo(name_to_set=f_name, obj=field))

    return fields


def get_fields_info(cls):
    fields = parse_fields(cls)
    subconfigs = [
        SubConfigInfo(name_to_set=t, obj=getattr(cls, t))
        for t in dir(cls)
        if type(getattr(cls, t)) is type and not is_dunder(t)
    ]
    fields.extend(subconfigs)
    return fields


def betterconf(
    cls=None,
    provider: AbstractProvider = DEFAULT_PROVIDER,
    prefix: typing.Optional[str] = None,
):

    def inner(cls):
        def our_init(
            self, _provider_: typing.Optional[AbstractProvider] = None, **to_override
        ):
            _provider = _provider_ or self._provider_
            self._init_fields(
                self._prefix_, self, _provider, _parser=get_fields_info, **to_override
            )

        cls._provider_ = provider
        cls._prefix_ = prefix

        cls.__init__ = our_init
        cls._init_fields = InternalConfig._init_fields

        return cls

    if cls is None:
        return inner

    return inner(cls)
