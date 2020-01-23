import typing

VT = typing.TypeVar("VT")


class AbstractCaster:
    def cast(self, val: str):
        """Try to cast or return val"""
        raise NotImplementedError()


class ConstantCaster(AbstractCaster, typing.Generic[VT]):

    ABLE_TO_CAST: typing.Dict[str, typing.Any] = {}

    def cast(self, val: str) -> typing.Union[str, VT]:
        """Cast using ABLE_TO_CAST dictionary as in BoolCaster"""
        converted = self.ABLE_TO_CAST.get(val.lower())
        if not converted:
            return val
        else:
            return converted


class BoolCaster(ConstantCaster):

    ABLE_TO_CAST = {"true": True, "false": False}


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
