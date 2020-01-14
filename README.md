# Minimalistic Python library for your configs.

Betterconf (**better config**) is a Python library for project configuration
managment. It allows you define your config like a regular Python class.

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

By default **betterconf** gets all values from `os.environ` but sometimes we need much.
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

Also we can cast our values to python objects (or just manipulate them):

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



## License
This project is licensed under MIT License.

See [LICENSE](LICENSE) for details.


Made with :heart: by [prostomarkeloff](https://github.com/prostomarkeloff) and our contributors.
