#!/usr/bin/env python3.7
import typing

from betterconf import Config
from betterconf import field
from betterconf.caster import to_int, to_bool, ConstantCaster
from betterconf.config import VariableNotFoundError


class BaseConfig(Config):
    debug = field(default=False, caster=to_bool)

    class AccountInfo:
        username = field("ACCOUNT_USERNAME")
        password = field("ACCOUNT_PASSWORD")
        id = field("ACCOUNT_ID", caster=to_int)

    class Integration:
        class SMTP:
            server = field(default='smtp.gmail.com')
            port = field(default='465')
            login = field()
            password = field()


class Prod(BaseConfig):
    __prefix__ = 'PROD'

    class Integration(BaseConfig.Integration):
        class SMTP(BaseConfig.Integration.SMTP):
            login = field(default='prod@gmail.com')
            password = field(default='123456')


class Test(BaseConfig):
    __prefix__ = 'TEST'

    debug = field(default=True, caster=to_bool)

    class Integration(BaseConfig.Integration):
        class SMTP(BaseConfig.Integration.SMTP):
            login = field(default='test@gmail.com')
            password = field(default='123456')


class TypeConfig(ConstantCaster):

    ABLE_TO_CAST = {"test": Test, 'prod': Prod}


if __name__ == "__main__":
    config: typing.Union[Test, Prod] = field('TYPE_CONFIG', caster=TypeConfig(), default=Test).value

    try:
        config.required_fields()
    except VariableNotFoundError as ex:
        print(ex.message)

    print(config.to_dict())
