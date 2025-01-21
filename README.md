# Configs in Python made smooth and simple

Betterconf (**better config**) is a Python library for project configuration
management. It allows you define your config like a regular Python class.

Features:

* Easy to hack.
* Less boilerplate.
* Minimal code to do big things.
* Zero dependencies. Only vanilla Python >=3.11

Betterconf is heavily typed, so your editors and typecheckers will be happy with it.

It's not that huge as Pydantic, so takes like 5 minutes to dive into.

Betterconf is highly customizable, so you can do anything with it.

## Installation

I recommend you to use poetry:

```sh
poetry add betterconf
```

However, you can use pip:

```sh
pip install betterconf
```

## How to?

Betterconf is very intuitive, so you don't need special knowledge to use it. We'll cover the basics.

The most simple config will look like this:
```python
from betterconf import betterconf

@betterconf
class Config:
    LOGIN: str
    PASSWORD: str

cfg = Config()
print(config.LOGIN)
```

Let's dive into what it does. By default, betterconf uses `EnvironmentProvider`, getting values with `os.getenv`,
so you can run this example with `LOGIN=vasya PASSWORD=admin python config.py` and simply get your login.


There is a very usable thing in our fancy-web-world, called `.env`s. Betterconf, since 4.5.0 automatically supports them out-of-the-box! See it:

```python
from betterconf import betterconf, DotenvProvider

# here betterconf gets values from `.env` file, you can change name or the path passing it as the first
# argument to provider.
# also, auto_load lets you not to write `provider.load_into_env` (loading variables to os.environ)
# or `provider.load_into_provider()` (loading them into the provider's inner storage).
@betterconf(provider=DotenvProvider(auto_load=True))
class Config:
    val1: int
    val2: str
    name: str

cfg = Config()
print(cfg.val1, cfg.val2, cfg.name)
```

Your `.env` then looks like this:

```
name="John Wicked"
val1=12
val2="testing value"
```


But what if you need a different provider? Betterconf lets you set providers as for config itself and for each field respectively.

```python
import json
from betterconf import Alias
from betterconf import betterconf, field
from betterconf import JSONProvider, AbstractProvider

sample_json_config = json.dumps({"field": {"from": {"json": 123}}})

# our provider, that just gives the name of field back
class NameProvider(AbstractProvider):
    def get(self, name: str) -> str:
        return name

@betterconf(provider=NameProvider())
class Config:
    # value will be got from NameProvider and will simply be `my_fancy_name`
    my_fancy_name: str
    # here we get value from JSONProvider; the default nested_access is '.'
    field_from_json: Alias[int, "field::from::json"] = field(provider=JSONProvider(sample_json_config, nested_access="::"))

```

Betterconf casts primitive types itself, they include list, float, str, int. But if you need specific caster, say for complex object, you can write your own.

```python
from betterconf import betterconf
from betterconf import AbstractCaster, field

class DashesToDotsCaster(AbstractCaster):
    def cast(self, val: str) -> str:
        return val.replace("_", ".")

@betterconf
class Config:
    simple_int: int
    value: str = field(caster=DashesToDotsCaster())

print(Config(value="privet_mir", simple_int="55666").value)
```

Subconfigs and referencing one field in another declaration is also available. Check out examples folder.

## License
This project is licensed under MIT License.

See [LICENSE](LICENSE) for details.


Made with :heart: by [prostomarkeloff](https://github.com/prostomarkeloff) and our contributors.
