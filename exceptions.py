class NoGamblerFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class CooldownException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class DuplicateGuessException(Exception):
    def __init__(self, *args):
        super().__init__(*args)