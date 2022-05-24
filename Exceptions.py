class UnlabeledDAT(Exception):
    def __init__(self, location):
        self.location = location

class UnknownInstruction(Exception):
    def __init__(self, location):
        self.location = location

class UnknownVariable(Exception):
    def __init__(self, location):
        self.location = location

class UnknownLocation(Exception):
    def __init__(self, location):
        self.location = location
