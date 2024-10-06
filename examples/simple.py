#!/usr/bin/env python3.7
from betterconf import betterconf
from betterconf import field
from betterconf.caster import to_int

@betterconf
class AccountInfo:
    username = field("ACCOUNT_USERNAME")
    password = field("ACCOUNT_PASSWORD")
    id: int = field("ACCOUNT_ID", caster=to_int)


if __name__ == "__main__":
    info = AccountInfo()
    print(
        f"Username is {info.username}, password is {info.password} and ID is {info.id}"
    )
