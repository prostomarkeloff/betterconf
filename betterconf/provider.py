import os
from betterconf.exceptions import VariableNotFoundError


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


DEFAULT_PROVIDER = EnvironmentProvider()
