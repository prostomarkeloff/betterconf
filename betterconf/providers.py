from configparser import ConfigParser
from typing import Union, Any, Tuple, List

DEFAULT_PROVIDER = EnvironmentProvider()

class AbstractProvider:
    """Implement this class and pass to `field`"""

    def get(self, name: str) -> typing.Any:
        """Return a value or None"""
        raise NotImplementedError()


class EnvironmentProvider(AbstractProvider):
    """Default provider. Gets vals from environment"""

    def get(self, name: str) -> typing.Any:
        return os.getenv(name)

class INIProvider(AbstractProvider):
    """Provider that gets values from .INI files"""

    def __init__(self, files: Union[str, List[str]],
                 delimiters: Tuple[str] = ('=', ':'),
                 comment_prefixes: Tuple[str] = ('#', ';')):
        self.cfg = ConfigParser(delimiters=delimiters, comment_prefixes=comment_prefixes)
        if isinstance(files, str):
            files = [files]
        self.cfg.read(files)

    def get(self, name: str) -> str:
        return self.cfg.get(name)
