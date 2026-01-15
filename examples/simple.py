from betterconf import betterconf
from betterconf import Alias


@betterconf(prefix="ACCOUNT")
class AccountInfo:
    username: Alias[str, "USERNAME"]
    password: Alias[str, "PASSWORD"]
    id: Alias[int, "ID"]


if __name__ == "__main__":
    info = AccountInfo()
    print(
        f"Username is {info.username}, password is {info.password} and ID is {info.id}"
    )
