class objectview(object):
    def __init__(self, d):
        self.__dict__ = d


for i in range(1, 10):
    print(i)
    if i == 5:
        break
    
print(i)