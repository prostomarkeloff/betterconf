import dataclasses
import typing

_T = typing.TypeVar("_T")
_T2 = typing.TypeVar("_T2")


class _Special:
    pass


def is_special(tp: typing.Any) -> bool:
    return isinstance(tp, _Special)


@dataclasses.dataclass(eq=True, frozen=True)
class AliasSpecial(_Special):
    tp: type
    alias: str

    @classmethod
    def __class_getitem__(cls, *args: typing.Tuple[type, str]) -> typing.Self:
        parsed = args[0]

        return cls(parsed[0], parsed[1])


if typing.TYPE_CHECKING:
    Alias = typing.Annotated

else:
    Alias = AliasSpecial
