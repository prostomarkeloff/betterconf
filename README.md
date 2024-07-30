# Minimalistic Python library for your configs.

Betterconf (**better config**) is a Python library for project configuration
management. It allows you define your config like a regular Python class.

Features:

* Easy to hack.
* Less boilerplate.
* Minimal code to do big things.

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

This is a guide written for betterconf 3.x, earlier versions can work differently

Try to write a simple config:
```python
from betterconf import field, Config

class MyConfig(Config):
    my_var = field("my_var")

cfg = MyConfig()
print(cfg.my_var)
```

Try to run:
```sh
my_var=1 python our_file.py
```

With default values:
```python
from betterconf import field, Config

class MyConfig(Config):
    my_var = field("my_var", default="hello world")
    my_second_var = field("my_second_var", default=lambda: "hi") # can be callable!

cfg = MyConfig()
print(cfg.my_var)
print(cfg.my_second_var)
# hello world
# hi
```

Override values when it's needed (for an example: test cases)
```python
from betterconf import field, Config

class MyConfig(Config):
    my_var = field("my_var", default="hello world")

cfg = MyConfig(my_var="WOW!")
print(cfg.my_var)
# WOW!
```

By default, **betterconf** gets all values from `os.environ` but sometimes we need more.
You can create own `field's value provider` in minutes:

```python
from betterconf import field, Config
from betterconf.config import AbstractProvider

class NameProvider(AbstractProvider):
    def get(self, name: str):
        return name

class Cfg(Config):
    my_var = field("my_var", provider=NameProvider())

cfg = Cfg()
print(cfg.my_var)
# my_var
```

You can specify the class' default provider manually:

```python
from betterconf import field, Config
from betterconf.config import AbstractProvider

class FancyNameProvider(AbstractProvider):
    def get(self, name: str) -> str:
        return f"fancy_{name}"
    
class Cfg(Config):
    _provider_ = FancyNameProvider()
    
    val1 = field("val1")
    val2 = field("val2")
    
cfg = Cfg()
print(cfg.val1, cfg.val2)
# fancy_val1, fancy_val2

# or you can change the provider at initialization moment
cfg = Cfg(_provider_=FancyNameProvider())
...

# However, this won't work with nested configs; their provider will be as it's set in `_provider_` field

```

Also, we can cast our values to python objects (or just manipulate them):

```python
from betterconf import field, Config
# out of the box we have `to_bool` and `to_int`
from betterconf.caster import to_bool, to_int, AbstractCaster


class DashToDotCaster(AbstractCaster):
    def cast(self, val: str):
        return val.replace("-", ".")

to_dot = DashToDotCaster()

class Cfg(Config):
    integer = field("integer", caster=to_int)
    boolean = field("boolean", caster=to_bool)
    dots = field("dashes", caster=to_dot)

cfg = Cfg()
print(cfg.integer, cfg.boolean, cfg.dots)
# -500, True, hello.world

```

```sh
integer=-500 boolean=true dashes=hello-world python our_file.py
```

Sometimes we need to reference one field value in another one.

```python
from betterconf import Config, field, reference_field
from betterconf.caster import to_int

class MyConfig(Config):
    money = field("MONEY_VAR", caster=to_int)
    name = field("NAME_VAR")
    
    money_if_a_lot: int = reference_field(money, func=lambda m: m * 1000)
    greeting: str = reference_field(money, name, func=lambda m, n: f"Hello, my name is {n} and I'm rich for {m}")
    
```

There is a builtin support for constant fields and getting field's value on-fly at any place of code:

```python
from betterconf import value, constant_field, Config
from betterconf.caster import to_int

class Constants(Config):
    admin_id: int = constant_field(1)
    timezone: str = constant_field("UTC+3")
    
debug: bool = value("DEBUG", default=True)
print("Current status of debbuging is ", debug)

# betterconf can be used as a casting framework!
val: int = value(default="123", caster=to_int)
assert val == 123

```


## License
This project is licensed under MIT License.

See [LICENSE](LICENSE) for details.


Made with :heart: by [prostomarkeloff](https://github.com/prostomarkeloff) and our contributors.
