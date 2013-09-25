class FakeObject:
    pass

class FakeModel:
    def __init__(self, xpaths):
        self.xpaths = dict(xpaths)

    def xpath(self, path):
        return self.xpaths[path]
