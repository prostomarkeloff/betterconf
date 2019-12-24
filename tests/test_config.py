import os

import pytest

from betterconf import Config
from betterconf import field

VAR_1 = "hello"
VAR_1_VALUE = "hello!#"


def test_not_exist():
    with pytest.raises(ValueError):

        class ConfigBad(Config):
            var1 = field(VAR_1)

        cfg = ConfigBad()


def test_exist():
    os.environ[VAR_1] = VAR_1_VALUE

    class ConfigGood(Config):
        var1 = field(VAR_1)

    cfg = ConfigGood()
    assert cfg.var1 == VAR_1_VALUE
