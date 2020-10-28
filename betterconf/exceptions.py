class BetterconfError(Exception):
    pass


class ImpossibleToCastError(BetterconfError):
    def __init__(self, val: str, caster: object):
        self.val = val
        self.caster_name = caster.__class__.__name__
        self.message = 'Could not cast "{}" with {}'.format(self.val, self.caster_name)
        super().__init__(self.message)


class VariableNotFoundError(BetterconfError):
    def __init__(self, variable_name: str):
        self.var_name = variable_name
        self.message = "Variable ({}) hasn't been found".format(variable_name)
        super().__init__(self.message)
