class BetterconfError(Exception):
    pass


class ImpossibleToCastError(BetterconfError):
    def __init__(self, val: str, caster: object):
        self.val = val
        self.caster = caster
        self.message = f'Could not cast "{val}" with {caster.__class__.__name__}'
        super().__init__(self.message)


class VariableNotFoundError(BetterconfError):
    def __init__(self, variable_name: str):
        self.variable_name = variable_name
        self.message = f"Variable ({variable_name}) hasn't been found"
        super().__init__(self.message)
