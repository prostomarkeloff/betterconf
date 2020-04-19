#!/usr/bin/env python3.7
import typing

from betterconf import Config
from betterconf import field
from betterconf.caster import to_bool, ConstantCaster
from betterconf.config import VariableNotFoundError, as_dict


class BaseConfig(Config):
    debug = field(default=False, caster=to_bool)

    class Integration:
        class SMTP:
            server = field(default='smtp.gmail.com')
            port = field(default='465')
            login = field()
            password = field()


class Prod(BaseConfig):
    _prefix_ = 'PROD'

    class Integration(BaseConfig.Integration):
        class SMTP(BaseConfig.Integration.SMTP):
            login = field(default='prod@gmail.com')
            password = field(default='123456')


class Test(BaseConfig):
    _prefix_ = 'TEST'

    debug = field(default=True, caster=to_bool)

    class Integration(BaseConfig.Integration):
        class SMTP(BaseConfig.Integration.SMTP):
            login = field(default='test@gmail.com')
            password = field(default='123456')


class TypeConfig(ConstantCaster):

    ABLE_TO_CAST = {"test": Test, 'prod': Prod}


if __name__ == "__main__":
    try:
        config: typing.Union[Test, Prod] = field('TYPE_CONFIG', caster=TypeConfig(), default=Test).value
        print(as_dict(config))
        print(f'Mode debug: {config.debug}. SMTP login: {config.Integration.SMTP.login}')
    except VariableNotFoundError as ex:
        print(ex.message)
