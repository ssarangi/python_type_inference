__author__ = 'sarangis'

class Value:
    def __init__(self):
        pass

class Argument(Value):
    def __init__(self, name):
        Value.__init__(self)
        self.__name = name
        self.uses = []

    @property
    def name(self):
        return self.__name

    def __str__(self):
        return self.__name

    __repr__ = __str__