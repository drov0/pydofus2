class objectview(object):
    def __init__(self, d):
        self.__dict__ = d


obj = objectview({"a": 1})
print(obj.a)
