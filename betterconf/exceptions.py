class BetterconfError(Exception):
    pass


class ImpossibleToCastError(BetterconfError):
    def __init__(self, val: str, caster: object):
        self.val = val
        self.caster = caster
        self.message = 'Could not cast "{}" with {}'.format(val, caster.__class__.__name__)
        super().__init__(self.message)


class VariableNotFoundError(BetterconfError):
    def __init__(self, variable_name: str):
        self.variable_name = variable_name
        self.message = "Variable ({}) hasn't been found".format(variable_name)
        super().__init__(self.message)
