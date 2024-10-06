import typing
from betterconf.provider import AbstractProvider, DEFAULT_PROVIDER
from betterconf._config import ConfigInner, ConfigProto, Prefix

class_T = typing.TypeVar("class_T", bound=type)


@typing.overload
def betterconf(
    cls: class_T,
    provider: typing.Optional[AbstractProvider] = None,
    prefix: typing.Optional[typing.Union[Prefix, str]] = None,
    subconfig: bool = False,
) -> class_T: ...


@typing.overload
def betterconf(
    cls: None = None,
    provider: typing.Optional[AbstractProvider] = None,
    prefix: typing.Optional[typing.Union[Prefix, str]] = None,
    subconfig: bool = False,
) -> typing.Callable[[class_T], class_T]: ...


def betterconf(
    cls: typing.Optional[class_T] = None,
    provider: typing.Optional[AbstractProvider] = None,
    prefix: typing.Optional[typing.Union[Prefix, str]] = None,
    subconfig: bool = False,
) -> typing.Union[class_T, typing.Callable[[class_T], class_T]]:
    def inner(cls: class_T) -> class_T:
        def __init__(
            self: ConfigProto,
            _provider_: typing.Optional[AbstractProvider] = None,
            **to_override: typing.Any,
        ):
            for field in self.__bc_inner__.fields:
                if not field.field.provider:
                    field.field.provider = provider

                if _provider_:
                    field.field.provider = _provider_

                if field.name_in_python in to_override:
                    field.field.default = to_override[field.name_in_python]
                    setattr(self, field.name_in_python, field.field.value)
                else:
                    setattr(self, field.name_in_python, field.field.value)

            for sub_config in self.__bc_inner__.sub_configs:
                if not sub_config.cfg.__bc_provider__:
                    sub_config.cfg.__bc_provider__ = provider

                if _provider_:
                    sub_config.cfg.__bc_provider__ = _provider_

                if sub_config.name in to_override:
                    setattr(self, sub_config.name, to_override[sub_config.name])
                else:
                    config = sub_config.cfg(**to_override)
                    setattr(self, sub_config.name, config)

        nonlocal provider
        if subconfig is False:
            provider = provider or DEFAULT_PROVIDER

        nonlocal prefix
        if isinstance(prefix, str):
            prefix = Prefix(prefix)

        cls.__bc_subconfig__ = subconfig
        cls.__bc_inner__ = ConfigInner.parse_into(cls, provider, prefix)
        cls.__bc_prefix__ = prefix
        cls.__bc_provider__ = provider

        setattr(cls, "__init__", __init__)
        return cls

    if cls is None:
        return inner

    return inner(cls)
