from betterconf import betterconf


@betterconf
class BaseConfig:
    debug: bool = False

    @betterconf(subconfig=True)
    class Integration:
        @betterconf(subconfig=True)
        class SMTP:
            server: str = "smtp.gmail.com"
            port: int = 465
            login: str
            password: str


@betterconf(prefix="PROD")
class Prod(BaseConfig):
    @betterconf(subconfig=True)
    class Integration(BaseConfig.Integration):
        @betterconf(subconfig=True)
        class SMTP(BaseConfig.Integration.SMTP):
            login: str = "prod@gmail.com"
            password: str = "123456"


@betterconf(prefix="TEST")
class Test(BaseConfig):
    debug: bool = True

    @betterconf(subconfig=True)
    class Integration(BaseConfig.Integration):
        @betterconf(subconfig=True)
        class SMTP(BaseConfig.Integration.SMTP):
            login: str = "test@gmail.com"
            password: str = "123456"
