from betterconf import Config, field, reference_field, compose_field
from betterconf.caster import to_int


class MoneyConfig(Config):
    money = field("MONEY_VAR", default=10, caster=to_int)
    name = field("NAME_VAR", default="Johnny")

    money_if_a_lot: int = reference_field(money, lambda m: m * 1000)
    greeting: str = compose_field(money, name, lambda m, n: f"Hello, my name is {n} and I'm rich for {m}")

if __name__ == "__main__":
    cfg = MoneyConfig()
    print(f"{cfg.greeting}. I could have ${cfg.money_if_a_lot}...")