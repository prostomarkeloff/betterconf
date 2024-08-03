import os

import pytest

from betterconf import Config
from betterconf import field
from betterconf.caster import (
    AbstractCaster,
    ConstantCaster,
    IntCaster,
    FloatCaster,
    ListCaster,
)
from betterconf.caster import to_bool, to_int, to_float, to_list
from betterconf.config import (
    AbstractProvider,
    Field,
    as_dict,
    reference_field,
    compose_field,
    value,
)
from betterconf.config import VariableNotFoundError
from betterconf.exceptions import ImpossibleToCastError

VAR_1 = "hello"
VAR_1_VALUE = "hello!#"


class TestConfig(Config):
    debug = field("DEBUG", default=False, caster=to_bool)

    class Sub1Config:
        class Sub2Config:
            config_1 = field(default="base.mail.com")
            config_2 = field(default="465")
            config_3 = field(default="test")


class ProdConfig(TestConfig):
    _prefix_ = "PROD"

    class Sub1Config(TestConfig.Sub1Config):
        class Sub2Config(TestConfig.Sub1Config.Sub2Config):
            config_1 = field(default="prod.mail.com")
            config_2 = field(default="465")


@pytest.fixture
def update_environ():
    os.environ["DEBUG"] = "true"
    os.environ["SUB1CONFIG_SUB2CONFIG_CONFIG_1"] = "test.mail.com"
    os.environ["PROD_SUB1CONFIG_SUB2CONFIG_CONFIG_2"] = "100202"
    os.environ["NONEFUL_FIELD"] = "None"
    os.environ["FALSY_FIELD"] = "0"
    yield
    os.environ.pop("DEBUG", None)
    os.environ.pop("SUB1CONFIG_SUB2CONFIG_CONFIG_1", None)
    os.environ.pop("PROD_SUB1CONFIG_SUB2CONFIG_CONFIG_2", None)


def test_negative_values(update_environ):
    caster = ConstantCaster()
    caster.ABLE_TO_CAST = dict(none=None)

    class NegativeConfig(Config):
        none = field("NONEFUL_FIELD", caster=caster)
        false = field("FALSY_FIELD", caster=to_int)

    cfg = NegativeConfig()
    assert cfg.none is None
    assert not cfg.false


def test_not_exist():
    class ConfigBad(Config):
        var1 = field(VAR_1)

    with pytest.raises(VariableNotFoundError):
        ConfigBad()


def test_reference_field():
    class ConfigWithRef2(Config):
        var1 = field("var1", default=lambda: {"hello": "world"})
        var2 = reference_field(var1, func=lambda v: v["hello"])

    cfg = ConfigWithRef2()
    assert cfg.var2 == "world"


def test_compose_field():
    class ConfigWithCompose(Config):
        var1 = field("var1", default="John")
        var2 = compose_field(
            field("var2", default="hello"),
            var1,
            lambda first, second: f"{first} {second}",
        )

    cfg = ConfigWithCompose()
    assert cfg.var2 == "hello John"


def test_experimental_basics(update_environ):
    from typing import Annotated
    from betterconf.experimental import betterconf
    from betterconf import field

    @betterconf
    class Config:
        # caster type, alias
        debug: Annotated[bool, "DEBUG"]
        value: str = field(default="LOL")
        meta = field(default=123)

    cfg = Config()
    assert cfg.debug is True
    assert cfg.value is not "lol"
    assert cfg.meta is 123


def test_json_provider():
    from typing import Annotated
    from betterconf.experimental import betterconf
    from betterconf.provider import JSONProvider
    import json

    data = json.dumps(
        {"DEBUG": True, "name": "Ilaja", "age": 15, "nested": {"status": True, }}
    )

    @betterconf(
        provider=JSONProvider.from_string(data, nested_access="::"),
    )
    class Config:
        debug: Annotated[bool, "DEBUG"]
        nested_status: Annotated[bool, "nested::status"]
        name: str
        age: int

    cfg = Config()
    assert cfg.debug is True
    assert cfg.name == "Ilaja"
    assert cfg.age > 10


def test_experimental_subconfigs(update_environ):
    from typing import Annotated
    from betterconf.experimental import betterconf
    from betterconf import constant_field

    @betterconf
    class Config:
        f = constant_field("ffff")

        class Sub:
            debug: Annotated[bool, "DEBUG"]

    cfg = Config()
    assert cfg.f == "ffff"
    assert cfg.Sub.debug is True


def test_multiple_compose_field():
    class ConfigWithCompose(Config):
        age = field("age", default=16, caster=to_int)
        name = field("name", default="John")
        greeting = compose_field(age, name, lambda a, n: f"My name is {n}. I'm {a}")
        dream = compose_field(
            greeting,
            reference_field(age, func=lambda a: a + 10),
            lambda f, s: f"When I was young I said '{f}', but now I'm {s} and I don't say that crap",
        )

    cfg = ConfigWithCompose()
    assert cfg.greeting == "My name is John. I'm 16"
    assert (
            cfg.dream
            == "When I was young I said 'My name is John. I'm 16', but now I'm 26 and I don't say that crap"
    )


def test_reference_to_override():
    class ConfigWithReference(Config):
        var1: int | Field = field("var1", default=4)
        var2: int = reference_field(var1, func=lambda v: v * 2)

    cfg1 = ConfigWithReference()
    assert cfg1.var2 == cfg1.var1 * 2

    cfg2 = ConfigWithReference(var1=15)
    assert cfg2.var2 == cfg2.var1 * 2


def test_default_provider_for_cfg():
    class FancyProvider(AbstractProvider):
        def get(self, name: str) -> str:
            return f"fancy_{name}"

    class SubFancyProvider(AbstractProvider):

        def get(self, name: str) -> str:
            return f"subfancy_{name}"

    class MyConfig(Config):
        _provider_ = FancyProvider()

        val: str = field("value")

        class SubConfig:
            _provider_ = SubFancyProvider()

            subval: str = field("value")

        class SubConfigWithoutProvider:
            val: str = field("value")

    cfg = MyConfig()
    assert cfg.val == "fancy_value"
    assert cfg.SubConfig.subval == "subfancy_value"
    assert cfg.SubConfigWithoutProvider.val == "fancy_value"


def test_instant_value(update_environ):
    v: bool = value("DEBUG", caster=to_bool)
    assert v is True


def test_reference_many_fields():
    class ConfigWithManyReferences(Config):
        var1: int | Field = field("var1", default=4)
        var2: int | Field = field("var2", default=5)
        var3: int | Field = field("var3", default=6)
        var4: int = reference_field(
            var1, var2, var3, func=lambda v1, v2, v3: v1 * 2 + v2 * 2 + v3 * 3
        )

    cfg = ConfigWithManyReferences()
    assert cfg.var4 == (cfg.var1 * 2 + cfg.var2 * 2 + cfg.var3 * 3)


def test_field_as_default():
    class ConfigWithDefaults(Config):
        var1 = field(default="Goyda")
        var2 = field(default=var1)

    cfg = ConfigWithDefaults()
    assert cfg.var1 == "Goyda"
    assert cfg.var2 == "Goyda"

    cfg = ConfigWithDefaults(var1="hmm")
    assert cfg.var1 == "hmm"
    assert cfg.var2 == "hmm"


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
            return name  # just return name of field =)

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


def test_default_name_field(update_environ):
    test_config = TestConfig()
    prod_config = ProdConfig()

    assert test_config.debug is True
    assert test_config.Sub1Config.Sub2Config.config_1 == "test.mail.com"
    assert prod_config.Sub1Config.Sub2Config.config_2 == "100202"


def test_required_fields():
    class BaseConfig(Config):
        config_1 = field()

    with pytest.raises(VariableNotFoundError):
        BaseConfig()


def test_fiend_name_is_none():
    with pytest.raises(VariableNotFoundError):
        Field().value()


def test_raise_abstract_provider():
    with pytest.raises(NotImplementedError):
        AbstractProvider().get("test")


def test_raise_abstract_caster():
    with pytest.raises(NotImplementedError):
        AbstractCaster().cast("test")


def test_constant_caster():
    constant_caster = ConstantCaster()

    constant_caster.ABLE_TO_CAST = {("key_1", "key_2"): "test"}
    assert constant_caster.cast("key_2") == "test"

    constant_caster.ABLE_TO_CAST = {"key_1": "test"}
    assert constant_caster.cast("Key_1") == "test"

    with pytest.raises(ImpossibleToCastError):
        assert constant_caster.cast("key")


def test_raises_int_caster():
    int_caster = IntCaster()
    with pytest.raises(ImpossibleToCastError):
        int_caster.cast("test")


def test_float_caster():
    float_caster = FloatCaster()
    assert float_caster.cast("3.14") == 3.14
    assert float_caster.cast("3,14") == 3.14

    with pytest.raises(ImpossibleToCastError):
        float_caster.cast("test")


def test_list_caster():
    list_caster = ListCaster()
    assert list_caster.cast("a") == ["a"]
    assert list_caster.cast("a,b,c") == ["a", "b", "c"]

    list_caster.separator = ";"
    assert list_caster.cast("a;b;c;") == ["a", "b", "c"]

    list_caster.separator = ", "
    assert list_caster.cast("a, b, c") == ["a", "b", "c"]
    assert list_caster.cast("a, b, c, ") == ["a", "b", "c"]


def test_to_dict():
    config = ProdConfig()

    assert as_dict(config) == {
        "_prefix_": "PROD",
        "_provider_": {},
        "Sub1Config": {
            "Sub2Config": {
                "config_1": "prod.mail.com",
                "config_2": "465",
                "config_3": "test",
            },
        },
        "debug": False,
    }
