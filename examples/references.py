from betterconf import betterconf, field, reference_field
from betterconf.caster import to_int


@betterconf
class MoneyConfig:
    money = field("MONEY_VAR", default=10, caster=to_int)
    name = field("NAME_VAR", default="Johnny")

    money_if_a_lot: int = reference_field(money, func=lambda m: m * 1000)
    greeting: str = reference_field(money, name, func=lambda m, n: f"Hello, my name is {n} and I'm rich for {m}")

if __name__ == "__main__":
    cfg = MoneyConfig()
    print(f"{cfg.greeting}. I could have ${cfg.money_if_a_lot}...")
