

class pageLink(object):
    '''
    we only maintain outDegree&destinations, excluding src
    update:  for Block-Strip Update alg. ,we must store src
    '''

    def __init__(self, src: int, deg: int, dests: [int]):
        self.src = src
        self.deg = deg
        self.dests = dests

    def __str__(self):
        return f"pageLink{{{self.src},{self.deg},{self.dests}}}"

    def toFileStr(self):
        res = str(self.src)+" "+str(self.deg)+" "
        for dest in self.dests:
            res += (str(dest)+" ")
        return res + "\n"
    # note: [page].__str__() will call page.__repr__()
    __repr__ = __str__


class page(object):
    def __init__(self, src, rank):
        self.src = src
        self.rank = rank

    def __lt__(self, rhs):
        return True if self.rank < rhs.rank else False

    def __str__(self):
        return f"{{{self.src},{self.rank}}}"

    __repr__ = __str__


def ToPages(data: []) -> [page]:
    res = []
    for v in data:
        res.append(page(v[0], v[1]))
    return res
