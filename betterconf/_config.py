import typing
from betterconf.provider import AbstractProvider
from betterconf._field import _NO_DEFAULT, _Field as Field  # type: ignore
from betterconf._specials import is_special, AliasSpecial
from betterconf.caster import BUILTIN_CASTERS
from dataclasses import dataclass
from betterconf.exceptions import BetterconfError

FT = typing.TypeVar("FT")


@dataclass
class Prefix:
    prefix: str
    delimiter: str = "_"

    @staticmethod
    def process_name(name: str, prefix: typing.Optional["Prefix"] = None) -> str:
        if not prefix:
            return name

        return f"{prefix.prefix}{prefix.delimiter}{name}"


class ConfigProto(typing.Protocol):
    __bc_subconfig__: typing.ClassVar[bool]
    __bc_inner__: typing.ClassVar["ConfigInner"]
    __bc_prefix__: typing.ClassVar[typing.Optional[Prefix]]
    __bc_provider__: typing.ClassVar[typing.Optional[AbstractProvider]]


@dataclass
class FieldInfo(typing.Generic[FT]):
    name_in_python: str
    field: Field[FT]

    @classmethod
    def parse_into(
        cls,
        src: type,
        name: str,
        annotation: FT,
        provider: typing.Optional[AbstractProvider] = None,
        prefix: typing.Optional[Prefix] = None,
    ) -> typing.Self:
        # for types like int, str, etc AND not initialized with `field`
        if annotation in BUILTIN_CASTERS and name not in src.__dict__:
            caster = BUILTIN_CASTERS[annotation]
            name_in_field = Prefix.process_name(name, prefix)
            return cls(
                name_in_python=name,
                field=Field(name=name_in_field, caster=caster, provider=provider),
            )

        # if it is our special annotations
        elif is_special(annotation):
            default = getattr(src, name, _NO_DEFAULT)

            if isinstance(annotation, AliasSpecial):
                name_in_field = Prefix.process_name(annotation.alias, prefix)

                field_info = cls.parse_into(
                    src, annotation.alias, annotation.tp, provider
                )
                field_info.name_in_python = name
                if isinstance(default, Field):
                    # var: Alias[str, "VAR"] = field(...)
                    field_info.field = default

                elif default is not _NO_DEFAULT:
                    field_info.field.default = default

                field_info.field.name = name_in_field

                if not field_info.field.provider:
                    field_info.field.provider = provider

                return field_info

        elif (
            annotation in BUILTIN_CASTERS
            and name in src.__dict__
            and isinstance(getattr(src, name), Field)
        ):
            field = typing.cast(Field[FT], getattr(src, name))
            field.caster = BUILTIN_CASTERS[annotation]

            if not field.provider:
                field.provider = provider
            if not field.name:
                field.name = name

            return cls(name_in_python=name, field=field)
        elif (
            annotation not in BUILTIN_CASTERS
            and name in src.__dict__
            and isinstance(getattr(src, name), Field)
        ):
            field: Field[FT] = getattr(src, name)
            if not field.provider:
                field.provider = provider
            if not field.name:
                field.name = name

            return cls(name_in_python=name, field=field)

        elif (
            annotation in BUILTIN_CASTERS
            and name in src.__dict__
            and isinstance(getattr(src, name), annotation)
        ):
            name_in_field = Prefix.process_name(name, prefix)
            val: typing.Any = getattr(src, name)
            field = Field(name=name_in_field, default=val, provider=provider)
            return cls(name_in_python=name, field=field)

        elif (
            annotation in BUILTIN_CASTERS
            and name in src.__dict__
            and not isinstance(getattr(src, name), annotation)
        ):
            raise BetterconfError(
                f"You try to set the value {repr(getattr(src, name))} for the field with name '{name}', that has type {annotation}.\nThe type {type(getattr(src, name))} is not assignable to type {annotation}"
            )

        raise BetterconfError(
            "Something bad happened.\nBetterconf can't deal with this kind of value.\nProbably you've tried to use something like 'dict' in a constant manner. For this special case use 'constant_field`"
        )


@dataclass
class SubConfigInfo:
    name: str
    cfg: typing.Type[ConfigProto]

    @classmethod
    def parse_into(
        cls,
        src: typing.Type[ConfigProto],
        provider: typing.Optional[AbstractProvider] = None,
        prefix: typing.Optional[Prefix] = None,
    ) -> typing.Self:
        if not src.__bc_provider__:
            src.__bc_provider__ = provider

        inner = ConfigInner.parse_into(src, provider, prefix)
        src.__bc_inner__ = inner
        return cls(name=src.__name__, cfg=src)


@dataclass
class ConfigInner:
    fields: typing.List[FieldInfo[typing.Any]]
    sub_configs: typing.List[SubConfigInfo]

    @classmethod
    def parse_into(
        cls,
        cfg: typing.Type[ConfigProto],
        provider: typing.Optional[AbstractProvider] = None,
        prefix: typing.Optional[Prefix] = None,
    ) -> typing.Self:
        try:
            annotations = typing.get_type_hints(cfg, include_extras=True)
        except TypeError:
            annotations = {}

        fields_info: typing.List[FieldInfo[typing.Any]] = []
        for name, annotation in annotations.items():
            parsed = FieldInfo[typing.Any].parse_into(
                cfg, name, annotation, provider, prefix
            )
            fields_info.append(parsed)

        sub_configs: typing.List[SubConfigInfo] = []

        for name, element in cfg.__dict__.items():
            if getattr(element, "__bc_subconfig__", False):
                parsed = SubConfigInfo.parse_into(element, provider, prefix)
                sub_configs.append(parsed)
            elif isinstance(element, Field):
                if element.name is None:
                    element.name = name

                fields_info.append(
                    FieldInfo(name, typing.cast(Field[typing.Any], element))
                )

        return cls(fields_info, sub_configs)
