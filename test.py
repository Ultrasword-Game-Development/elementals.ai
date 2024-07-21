






class A:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __hash__(self):
        return hash((self.a, self.b))






