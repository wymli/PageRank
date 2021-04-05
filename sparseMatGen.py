from rawMatGen import rawMat
import rawMatGen
from ITransferMat import ITransferMat


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

    def __init__(self, rawMat: rawMat, block=1):
        '''
        if rawMat == int, we will generate sparseMat directly,
        and generally,we should let rawMat == int,in order to avoiding OOM,
        otherwise if we have enough memory,we can let rawMat be a real 2d-array
        '''
        if isinstance(rawMat, int):
            self.size_ = rawMat
            self.pageLinks = sparseMat.GenBlockPageLinks(self.size_, block)
            return

        self.size_ = rawMat.size()
        if block == None or block == 1:
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
        deprecated: rawMat is huge,causing OOM, and it it is very slow to iterate it
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
        deprecated: rawMat is huge,causing OOM, and it it is very slow to iterate it
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
    def GenBlockPageLinks(size: int, block: int) -> [blockPageLink]:
        '''
        we must get a normal [pagelink] first, and then derive a [blockpagelink],
        it is impossible to get a [blockpagelink] from random
        '''
        pageLinks = []
        for c in range(size):
            dests = rawMatGen.getOneColDests(size)
            deg = len(dests)
            pageLinks.append(pageLink(c, deg, dests))

        # if block == 1,it means we don't need to block,so return directly
        if block == 1:
            return pageLinks
        # otherwise, we should change it to blockpagelinks
        return sparseMat.PageLinks2Block(pageLinks,block)
    
    @staticmethod
    def PageLinks2Block(pageLinks:[pageLink],block)->[blockPageLink]:
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
