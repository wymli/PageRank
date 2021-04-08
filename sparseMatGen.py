from rawMatGen import rawMat
import rawMatGen
from ITransferMat import ITransferMat
import metric


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
        return f"pl{{{self.src},{self.deg},{self.dests}}}"

    # note: [page].__str__() will call page.__repr__()
    __repr__ = __str__


class blockPageLink(object):
    def __init__(self, pageLinks: [pageLink]):
        self.pageLinks = pageLinks

    def __str__(self):
        return f"blockpl{{{self.pageLinks}}}"

    __repr__ = __str__


class sparseMat(ITransferMat):

    def __init__(self, rawMat: rawMat, block=1, version=3):
        '''
        if type(rawMat) is int,we will generate sparseMat from random\n
        if type(rawMat) is 2d-array,we will generate sparseMat from origin rawMat\n
        generally,type(rawMat) should be int, avoiding OOM
        '''
        # todo: judge version first,e.g. switch version{case 3:... case 2:... case 1:...}
        if isinstance(rawMat, int):
            self.size_ = rawMat
            # if we need to block,we just generate [blockpagelink] fron random directly
            if version == 3 and block != 1:
                self.pageLinks = sparseMat.GenBlockPageLinks(self.size_, block)
                return

            # the following code will generate [pagelink] first,and then generate [blockpagelink] from [pagelink]
            # generally, it is deprecated,only used when we don't want to block
            self.pageLinks = sparseMat.GenPageLinks(self.size_)
            if version == 2 and block != 1:
                self.pageLinks = sparseMat.PageLinks2Block(
                    self.pageLinks, block)
            return

        # the following code is deprecated,only used when rawMat is a 2d-array
        if version != 1:
            raise "unknown version"
        self.size_ = rawMat.size()
        if block == 1:
            self.pageLinks = sparseMat.ToPageLinks(rawMat)
        else:
            self.pageLinks = sparseMat.ToBlockPageLinks(rawMat, block)

    def size(self):
        return self.size_

    def __len__(self):
        return self.size_

    @staticmethod
    def ToPageLinks(rawMat: rawMat) -> [pageLink]:
        '''
        deprecated:
        从原始二维矩阵生成稀疏矩阵,OOM
        '''
        pageLinks = []
        size = rawMat.size()
        for c in range(size):
            dests = []
            for r in range(size):
                if rawMat[r][c] != 0:
                    dests.append(r)
            pageLinks.append(pageLink(c, rawMat.degs[c], dests))
        return pageLinks

    @staticmethod
    def ToBlockPageLinks(rawMat: rawMat, block: int) -> [blockPageLink]:
        '''
        deprecated: 
        从原始二维矩阵生成分块的稀疏矩阵,OOM
        '''
        size = rawMat.size()
        n = (size+block-1) // block  # ceil(rawMat / block)
        blockPageLinks = []
        for i in range(n):
            curBlock = range(i*block, min((i+1)*block, size))
            pageLinks = []
            for c in range(size):
                dests = []
                for r in curBlock:
                    if rawMat[r][c] != 0:
                        dests.append(r)
                pageLinks.append(pageLink(c, rawMat.degs[c], dests))
            blockPageLinks.append(blockPageLink(pageLinks))
        return blockPageLinks

    @staticmethod
    def GenPageLinks(size: int) -> [blockPageLink]:
        '''
        deprecated:
        直接从随机数生成原始的稀疏转移矩阵
        '''
        pageLinks = []
        for c in range(size):
            dests = rawMatGen.getOneColDests(size)
            deg = len(dests)
            pageLinks.append(pageLink(c, deg, dests))

        return pageLinks

    @staticmethod
    def PageLinks2Block(pageLinks: [pageLink], block) -> [blockPageLink]:
        '''
        deprecated:
        将原始的稀疏转移矩阵转换成分块的稀疏转移矩阵,迭代太慢
        '''
        size = len(pageLinks)
        n = (size+block-1) // block  # ceil(rawMat / block)
        blockPageLinks = []
        for i in range(n):
            curBlock = range(i*block, min((i+1)*block, size))
            pageLinksInBlock = []
            for c in range(size):
                dests = []
                for r in curBlock:
                    # print(f"size:{size},c:{c} r:{r}")
                    if r in pageLinks[c].dests:
                        dests.append(r)
                pageLinksInBlock.append(pageLink(c, pageLinks[c].deg, dests))
            blockPageLinks.append(blockPageLink(pageLinksInBlock))
        return blockPageLinks

    @staticmethod
    @metric.printTimeElapsed
    def GenBlockPageLinks(size, block):
        '''
        直接从随机数生成分块的稀疏转移矩阵
        '''
        n = (size+block-1) // block  # ceil(N / block)
        blockPageLinks = [blockPageLink([]) for _ in range(n)]
        for c in range(size):
            dests = rawMatGen.getOneColDests(size)
            deg = len(dests)
            for dest in dests:
                store = blockPageLinks[dest//block].pageLinks
                find = False
                for i, pl in enumerate(store):
                    if pl.src == c:
                        store[i].dests.append(dest)
                        find = True
                        break
                if not find:
                    store.append(pageLink(c, deg, [dest]))

        return blockPageLinks

    def getPageLink(self, i) -> pageLink:
        return self.pageLinks[i]

    def getBlockPageLink(self, i) -> blockPageLink:
        return self.pageLinks[i]


def TestToSparse():
    mat = sparseMat([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print(mat.pageLinks)


def Test():
    TestToSparse()


if __name__ == "__main__":
    Test()
