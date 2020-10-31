class AbstractProvider:
    """Implement this class and pass to `field`"""

    def get(self, name: str) -> typing.Any:
        """Return a value or None"""
        raise NotImplementedError()


class EnvironmentProvider(AbstractProvider):
    """Default provider. Gets vals from environment"""

    def get(self, name: str) -> typing.Any:
        return os.getenv(name)