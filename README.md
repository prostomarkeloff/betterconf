# Python configs for humans.
> Using OS environment.

Before you ask - this library doesn't support type-casts and other features. Just env parsing.

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