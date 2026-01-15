import json
import typing
from betterconf import (
    betterconf,
    field,
    JSONProvider,
    AbstractCaster,
    ImpossibleToCastError,
)
from dataclasses import dataclass


@dataclass
class UserData:
    login: str
    password: str
    user_id: int


class UserDataCaster(AbstractCaster):
    def cast(self, val: str) -> typing.Union[typing.Any, typing.NoReturn]:
        try:
            parsed = json.loads(val)
            return UserData(**parsed)
        except (json.JSONDecodeError, TypeError):
            raise ImpossibleToCastError(val, self)


pretend_config = json.dumps(
    {"id": 14, "user": {"login": "admin", "password": "admin", "user_id": 1}}
)


@betterconf(provider=JSONProvider(pretend_config))
class Config:
    id: int
    user: UserData = field(caster=UserDataCaster())


cfg = Config()
print(
    f"Id is {cfg.id}\nUser data: {cfg.user.login}:{cfg.user.password}|{cfg.user.user_id}"
)
