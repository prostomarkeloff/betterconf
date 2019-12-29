import os

import pytest

from betterconf import Config
from betterconf import field

VAR_1 = "hello"
VAR_1_VALUE = "hello!#"


def test_not_exist():
    class ConfigBad(Config):
        var1 = field(VAR_1)

    with pytest.raises(ValueError):
        cfg = ConfigBad()


def test_exist():
    os.environ[VAR_1] = VAR_1_VALUE

    class ConfigGood(Config):
        var1 = field(VAR_1)

    cfg = ConfigGood()
    assert cfg.var1 == VAR_1_VALUE


def test_default():
    class ConfigDefault(Config):
        var1 = field("var_1", default="var_1 value")

    cfg = ConfigDefault()
    assert cfg.var1 == "var_1 value"


def test_override():
    class ConfigOverride(Config):
        var1 = field("var_1", default=1)

    cfg = ConfigOverride(var1=100000)
    assert cfg.var1 == 100000
