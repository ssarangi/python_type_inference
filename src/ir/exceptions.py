__author__ = 'sarangis'

class IllegalArgumentException(ValueError):
    pass

class InvalidTypeException(ValueError):
    pass

class InvalidInsertionPointException(ValueError):
    pass

class InvalidInstructionException(ValueError):
    pass

class NoBBTerminatorException(ValueError):
    pass

class InvalidUsageModel(ValueError):
    pass

class PassNotRunException(ValueError):
    pass