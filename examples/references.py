from betterconf import betterconf, reference_field, field
from betterconf import Alias


@betterconf
class MoneyConfig:
    money: Alias[int, "MONEY_VAR"] = 10
    name = field("NAME_VAR", default="Johnny")

    money_if_a_lot: int = reference_field(money, func=lambda m: m * 1000)
    greeting: str = reference_field(money, name, func=lambda m, n: f"Hello, my name is {n} and I'm rich for {m}")

if __name__ == "__main__":
    cfg = MoneyConfig()
    print(f"{cfg.greeting}. I could have ${cfg.money_if_a_lot}...")
