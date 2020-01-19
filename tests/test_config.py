import os

import pytest

from betterconf import Config
from betterconf import field
from betterconf.caster import AbstractCaster
from betterconf.caster import to_bool
from betterconf.caster import to_int
from betterconf.config import AbstractProvider
from betterconf.config import VariableNotFoundError

VAR_1 = "hello"
VAR_1_VALUE = "hello!#"


def test_not_exist():
    class ConfigBad(Config):
        var1 = field(VAR_1)

    with pytest.raises(VariableNotFoundError):
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
        var2 = field("var_2", default=lambda: "callable var_2")

    cfg = ConfigDefault()
    assert cfg.var1 == "var_1 value"
    assert cfg.var2 == "callable var_2"


def test_override():
    class ConfigOverride(Config):
        var1 = field("var_1", default=1)

    cfg = ConfigOverride(var1=100000)
    assert cfg.var1 == 100000


def test_own_provider():
    class MyProvider(AbstractProvider):
        def get(self, name: str):
            return name  # just return name of filed =)

    provider = MyProvider()

    class ConfigWithMyProvider(Config):
        var1 = field("var_1", provider=provider)

    cfg = ConfigWithMyProvider()
    assert cfg.var1 == "var_1"


def test_bundled_casters():
    os.environ["boolean"] = "true"
    os.environ["integer"] = "-543"

    class MyConfig(Config):
        boolean = field("boolean", caster=to_bool)
        integer = field("integer", caster=to_int)

    cfg = MyConfig()
    assert cfg.boolean is True
    assert cfg.integer == -543


def test_own_caster():
    os.environ["text-with-dashes"] = "text-with-dashes"

    class DashToDotCaster(AbstractCaster):
        def cast(self, val: str):
            val = val.replace("-", ".")
            return val

    to_dot = DashToDotCaster()

    class MyConfig(Config):
        text = field("text-with-dashes", caster=to_dot)

    cfg = MyConfig()
    assert cfg.text == "text.with.dashes"
