import os
import json
import typing

from pathlib import Path
from betterconf.exceptions import BetterconfError, VariableNotFoundError


class AbstractProvider:
    """Implement this class and pass to `field`"""

    def get(self, name: str) -> str:
        """Return a value (str) or raise a `VariableNotFoundError`"""
        raise NotImplementedError()


class EnvironmentProvider(AbstractProvider):
    """Default provider. Gets vals from environment"""

    def get(self, name: str) -> str:
        value = os.getenv(name)
        if value is None:
            raise VariableNotFoundError(name)
        return value


class JSONProvider(AbstractProvider):
    @staticmethod
    def __bool_object_hook(inp: typing.Any) -> typing.Dict[typing.Any, typing.Any]:
        d: typing.Dict[typing.Any, typing.Any] = {}
        for k, v in inp.items():
            if isinstance(v, bool):
                d[k] = str(v)
                continue
            elif isinstance(v, list):
                d[k] = json.dumps(v)
                continue
            d[k] = v
        return d

    def __init__(self, inp: str, nested_access: str = "."):
        # dirty hack cause betterconf itself deserializes objects and we have to implement clear interface based on
        # str`s
        self._content: typing.Union[typing.Any, typing.Dict[str, typing.Any]] = (
            json.loads(
                inp,
                object_hook=self.__bool_object_hook,
                parse_int=lambda i: i,
                parse_float=lambda f: f,
                parse_constant=lambda c: c,
            )
        )
        self._nested_access = nested_access
        if not isinstance(self._content, dict):
            raise ValueError("JSONProvider doesn't know how to operate not on dicts")

    @classmethod
    def from_path(cls, path: str, nested_access: str = ".") -> typing.Self:
        return cls.from_file(open(path, mode="r"), nested_access)

    @classmethod
    def from_file(cls, file: typing.IO[str], nested_access: str = ".") -> typing.Self:
        contents = file.read()
        file.close()
        return cls(contents, nested_access)

    @classmethod
    def from_string(cls, inp: str, nested_access: str = "."):
        return cls(inp, nested_access)

    def get(self, name: str) -> str:
        nested = name.split(self._nested_access)
        result: typing.Optional[str] = None
        storage = self._content

        "hello.world == {'hello': {'world': 123}'"
        for k in nested:
            result = storage.get(k)  # type: ignore
            storage = result  # type: ignore

        if result is None or not isinstance(result, str):
            raise VariableNotFoundError(name)

        return result


class DotenvProvider(AbstractProvider):
    def __init__(
        self, file_path: str | Path = ".env", *, auto_load: bool = False
    ) -> None:
        self.file_path = file_path
        self._loaded_into: typing.Literal["env", "in", None] = None

        self._environ = EnvironmentProvider()
        self._inner: dict[str, str] = {}

        self._auto_load = auto_load

    def _put_lines_to_vars(self, into: typing.Literal["env", "in"]):
        with open(self.file_path, "r") as f:
            lines = f.readlines()

        vars: dict[str, str] = {}
        for line in lines:
            if line == "\n":
                continue
            try:
                var_name, var_value = line.split("=", 1)
            except ValueError:
                raise BetterconfError(
                    "DotenvProvider can't read your dotenv file because it seems to be broken"
                )

            var_value = var_value.rstrip("\n")
            var_name = var_name.rstrip("\n")
            vars[var_name] = var_value

        self._loaded_into = into
        if into == "in":
            self._inner.update(vars)
        elif into == "env":
            os.environ.update(vars)

    def load_into_env(self):
        self._put_lines_to_vars(into="env")

    def load_into_provider(self):
        self._put_lines_to_vars(into="in")

    def get(self, name: str) -> str:
        if self._auto_load and not self._loaded_into:
            self.load_into_provider()

        if not self._loaded_into:
            raise BetterconfError("You haven't loaded values from .env manually")

        if self._loaded_into == "in":
            value = self._inner.get(name)
            if value is None:
                raise VariableNotFoundError(name)
            return value
        else:
            return self._environ.get(name)


DEFAULT_PROVIDER = EnvironmentProvider()
