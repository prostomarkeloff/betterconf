import typing

VT = typing.TypeVar("VT")


class AbstractCaster:
    def cast(self, val: str) -> typing.Any:
        """Try to cast or return val"""
        raise NotImplementedError()


class ConstantCaster(AbstractCaster, typing.Generic[VT]):

    ABLE_TO_CAST: typing.Dict[
        typing.Union[str, typing.Tuple[str, ...]], typing.Any
    ] = {}

    def cast(self, val: str) -> typing.Union[str, VT]:
        """Cast using ABLE_TO_CAST dictionary as in BoolCaster"""
        if val in self.ABLE_TO_CAST:
            converted = self.ABLE_TO_CAST.get(val.lower())
            converted = typing.cast(VT, converted)
            return converted
        else:
            for key in self.ABLE_TO_CAST:
                if isinstance(key, tuple) and val.lower() in key:
                    return self.ABLE_TO_CAST[key]
                elif isinstance(key, str) and val.lower() == key:
                    return self.ABLE_TO_CAST[key]
            return val


class BoolCaster(ConstantCaster):

    ABLE_TO_CAST = {
        "true": True,
        "1": True,
        "yes": True,
        "ok": True,
        "on": True,
        "false": False,
        "0": False,
        "no": False,
        "off": False,
    }


class IntCaster(AbstractCaster):
    def cast(self, val: str) -> typing.Union[str, int]:
        try:
            as_int = int(val)
            return as_int
        except ValueError:
            return val


class NothingCaster(AbstractCaster):
    """Caster who does nothing"""

    def cast(self, val: str) -> str:
        return val


to_bool = BoolCaster()
to_int = IntCaster()
DEFAULT_CASTER = NothingCaster()

__all__ = ("to_bool", "to_int", "AbstractCaster", "ConstantCaster", "DEFAULT_CASTER")
