from rawMatGen import rawMat
import rawMatGen
from ITransferMat import ITransferMat
import metric
from os import path
import os
import itertools

mock = False


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


class blockPageLink(object):
    def __init__(self, pageLinks: [pageLink]):
        self.pageLinks = pageLinks

    def __str__(self):
        return f"blockpl{{{self.pageLinks}}}"

    def toFileStr(self):
        res = ""
        for pl in self.pageLinks:
            res += pl.toFileStr()
        return res

    __repr__ = __str__


class sparseMat(ITransferMat):

    def __init__(self, rawMat: rawMat, block=1, version=3, storeDir="./tmp/transferMat"):
        '''
        if type(rawMat) is int,we will generate sparseMat from random\n
        if type(rawMat) is rawMatGen.rawMat(2d-array),we will generate sparseMat from origin rawMat\n
        \n
        about version:\n
        version=3: we will generate blockedSparseMat directly from random\n
        version=2: we will generate unBlockedSparseMat directly from random,and convert it to blockedSparseMat\n
        version=1: we will convert 2d-array rawMat to blocked or unblocked sparseMat\n
        \n
        in practice:\n
        version=2 is proved slow to convert blockedSparseMat from unblockedSparseMat\n 
        version=1 is proved OOM to owm a large im-memory RawMat and conversion is alse slow\n
        \n
        todo: \n
        now we will allocate memory for sparseMat, and then store it to the file,\n
        obviously we should store it to the file directly 
        '''
        if not path.isdir(storeDir):
            os.makedirs(storeDir)
        self.block = block
        self.storeDir = storeDir
        self.blockFp = None
        self.indexFp = None
        print("\033[1;34m>>Using version:", version, end="\t")
        if version == 3:
            print("generate blocked/unblocked sparseMat from random")
            if not isinstance(rawMat, int):
                raise "rawMat should be int in version 3"
            self.size_ = rawMat
            # we just generate [blockpagelink] fron random directly
            # if block == 1,we won't block
            self.pageLinks = sparseMat.RandomGenSparse(self.size_, block)
        elif version == 2:
            # deprecated:
            # the following code will generate [pagelink] first,
            # and then generate [blockpagelink] from [pagelink]
            print(
                "generate blocked sparseMat from unblocked sparseMat(which is from random directly)")
            if not isinstance(rawMat, int):
                raise "rawMat should be int in version 2"
            self.size_ = rawMat
            self.pageLinks = sparseMat.GenPageLinks(self.size_)
            if block != 1:
                self.pageLinks = sparseMat.PageLinks2Block(
                    self.pageLinks, block)
        elif version == 1:
            # deprecated:
            # the following code is only used when rawMat is a 2d-array(rawMatGen.rawMat)
            print("generate blocked/unblocked sparseMat from rawMat")
            if not isinstance(rawMat, rawMatGen.rawMat):
                raise "rawMat should be [] in version 1"
            self.size_ = rawMat.size()
            self.pageLinks = sparseMat.RawMatToSparse(rawMat, block)

        print("<<\033[0m")
        # 如果不用内存模拟,并且矩阵分块,则持久化.
        # 如果不分块,是block-based method
        if not mock and self.block != 1:
            self.storeBlockPageLink()

    def size(self):
        return self.size_

    def __len__(self):
        return self.size_

    @staticmethod
    def RawMatToSparse(rawMat: rawMat, block: int) -> []:
        if block == 1:
            return sparseMat.ToPageLinks(rawMat)
        else:
            return sparseMat.ToBlockPageLinks(rawMat, block)

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
    def RandomGenSparse(size: int, block: int) -> []:
        if block == 1:
            return sparseMat.GenPageLinks(size)
        else:
            return sparseMat.GenBlockPageLinks(size, block)

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

    def getBlockPageLink(self, i) -> [pageLink]:
        '''
        load in-memory data if mock == true,otherwise load in-file data
        '''
        # a patch for iterBlock:
        # u will see the error if u run the program with rankBlock=2 and transferMatBlock=1(block-based method)
        if self.block == 1:
            return self.pageLinks
        # when using block-strip method,we should return a block
        if mock:
            return self.pageLinks[i].pageLinks
        return self.loadBlockPageLink(i).pageLinks

    def loadBlockPageLink(self, i):
        '''
        read data from file, it will be called in getBlockPageLink
        '''
        # 如果不分块,那么transferMat将存在于内存中,而无需持久化,这是block-based pagerank
        if self.block == 1:
            return blockPageLink(self.pageLinks)
        if i == 0:
            if self.blockFp != None:
                self.blockFp.seek(0)
            else:
                self.blockFp = open(path.join(self.storeDir, f"block"), "r")
            if self.indexFp != None:
                self.indexFp.seek(0)
            else:
                self.indexFp = open(path.join(self.storeDir, f"index"), "r")

        blockLen = int(self.indexFp.readline())
        pls = []
        for line in itertools.islice(self.blockFp, blockLen):
            nums = list(map(int, line.split()))
            pl = pageLink(nums[0], nums[1], nums[2:])
            pls.append(pl)
        return blockPageLink(pls)

    def storeBlockPageLink(self):
        '''
        将数据存在两个文件:block和index,index存每个block的长度
        '''
        with open(path.join(self.storeDir, "index"), "w") as f:
            f.writelines([str(len(bpl.pageLinks)) +
                          "\n" for bpl in self.pageLinks])
        with open(path.join(self.storeDir, "block"), "w") as f:
            for bpl in self.pageLinks:
                f.write(bpl.toFileStr())

    @staticmethod
    def extendFile(fp, data: []):
        fp.writelines(data)


def TestToSparse():
    mat = sparseMat([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print(mat.pageLinks)


def Test():
    TestToSparse()


if __name__ == "__main__":
    Test()
