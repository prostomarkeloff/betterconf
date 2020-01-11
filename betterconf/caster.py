import typing


class AbstractCaster:
    def cast(self, val: str):
        """Try to cast or return val"""
        raise NotImplementedError()


class BoolCaster(AbstractCaster):

    ABLE_TO_CAST = {"true": True, "false": False}

    def cast(self, val: str) -> typing.Union[str, bool]:
        as_bool = self.ABLE_TO_CAST.get(val.lower())
        if not as_bool:
            return val
        else:
            return as_bool


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

__all__ = ("to_bool", "to_int", "AbstractCaster", "DEFAULT_CASTER")
