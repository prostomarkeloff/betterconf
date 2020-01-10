# Minimalistic Python library for your configs.

## How to?
At first, install libary:

```sh
pip install betterconf
```

And... write simple config:
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

cfg = MyConfig()
print(cfg.my_var)
# hello world
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

By default `betterconf` gets all values from `os.environ` but sometimes we need much.
You can create own `field value provider` in minutes:

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
