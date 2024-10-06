from betterconf import betterconf, Prefix
from betterconf import field
from betterconf.caster import to_bool

@betterconf
class BaseConfig:
    debug = field(default=False, caster=to_bool)

    @betterconf(subconfig=True)
    class Integration:
        @betterconf(subconfig=True)
        class SMTP:
            server = field(default='smtp.gmail.com')
            port = field(default='465')
            login = field()
            password = field()

@betterconf(prefix=Prefix("PROD"))
class Prod(BaseConfig):
    @betterconf(subconfig=True)
    class Integration(BaseConfig.Integration):
        @betterconf(subconfig=True)
        class SMTP(BaseConfig.Integration.SMTP):
            login = field(default='prod@gmail.com')
            password = field(default='123456')


@betterconf(prefix=Prefix("TEST"))
class Test(BaseConfig):
    debug = field(default=True, caster=to_bool)

    @betterconf(subconfig=True)
    class Integration(BaseConfig.Integration):
        @betterconf(subconfig=True)
        class SMTP(BaseConfig.Integration.SMTP):
            login = field(default='test@gmail.com')
            password = field(default='123456')
