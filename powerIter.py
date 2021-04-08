from sparseMatGen import sparseMat
from ITransferMat import ITransferMat
import metric
import heapq
import json


class page(object):
    def __init__(self, src, rank):
        self.src = src
        self.rank = rank

    def __lt__(self, rhs):
        return True if self.rank < rhs.rank else False

    def __str__(self):
        return f"{{{self.src},{self.rank}}}"

    __repr__ = __str__


class pageRank(object):
    def __init__(self, transferMat: ITransferMat, beta: float, block: int = 1, storeDir: str = "."):
        '''
        1-beta : the rate of tp;\n
        block: the number of pages in one block;
        '''
        self.size = transferMat.size()
        self.rank = [1./self.size for _ in range(self.size)]
        self.oldRank = [-999 for _ in range(self.size)]
        self.mat = transferMat
        self.beta = beta
        self.block = block
        self.preVal = (1.-self.beta)/self.size
        self.storeDir = storeDir

    def loadRank(self, block: int, type: str) -> []:
        '''
        we will load data from storeDir
        if block == 1 ,we won't block i.e. return a origin rank list,otherwise return a block-based rank list
        \n
        todo: write a decoder generater,which yield a block from file each iter.
        we must implement it ourselves, because we only want to read one block into memory one time
        '''
        if type == "new":
            if block == 1:
                return self.rank.copy()
            else:
                iterCnt = (self.size+block-1) // block
                return [self.rank[block*i: min(block*(i+1), self.size)].copy() for i in range(iterCnt)]
        elif type == "old":
            if block == 1:
                return self.oldRank.copy()
            else:
                iterCnt = (self.size+block-1) // block
                return [self.oldRank[block*i: min(block*(i+1), self.size)].copy() for i in range(iterCnt)]
        else:
            raise "type not inplemented"

    def loadNewRank(self, block: int = 1) -> []:
        return self.loadRank(block, "new")

    def loadOldRank(self, block: int = 1) -> []:
        return self.loadRank(block, "old")

    def storeRank(self, rank: [], type: str):
        '''
        we will store data to storeDir
        \n
        todo: add a encoder ,write the encoded str/binary to file
        '''
        if type == "new":
            self.rank = rank
            # json.dumps(self.rank)
            return
        elif type == "old":
            self.oldRank = rank
            return
        else:
            raise "type not inplemented"

    def storeNewRank(self, rank: []):
        self.storeRank(rank, "new")

    def storeOldRank(self, rank: []):
        self.storeRank(rank, "old")

    def extendNewRank(self, rank: []):
        '''
        only append it to "new",typically it will append one block rank to rankFile
        \n
        todo: add a encoder ,append the encoded str/binary to the file\n
        if you use json, you should remove the last "}" in the file ,
        and then append this encoded str of the block,and then add "}" to make a close
        '''
        self.rank.extend(rank)
        return

    @metric.printTimeElapsed
    def iter(self, block):
        '''
        iter will call a plain powerIteration without block if param block=1
        otherwise it will call iterBlock
        '''
        if block != 1:
            self.iterBlock()
            return

        newRank = [self.preVal for _ in range(self.size)]
        oldRank = self.loadNewRank()

        for i in range(self.size):
            pl = self.mat.getPageLink(i)
            for dest in pl.dests:
                newRank[dest] += self.beta * oldRank[pl.src] / pl.deg

        self.storeNewRank(newRank)
        # todo:for efficiency, we can just rename the file,instead of writing back again
        self.storeOldRank(oldRank)

    @metric.printTimeElapsed
    def iterBlock(self):
        '''
        this is a kind of Block Stripe pagerank
        '''
        oldRank = self.loadNewRank()
        n = (self.size+self.block-1) // self.block  # ceil(rawMat / block)
        self.rank = []
        for i in range(n):
            curBlockLen = min((i+1)*self.block, self.size) - i*self.block
            newBlockRank = [self.preVal for _ in range(curBlockLen)]
            blockPL = self.mat.getBlockPageLink(i).pageLinks
            for pl in blockPL:
                for dest in pl.dests:
                    # print("dest:", dest, "block:", self.block,
                    #       "curBlocklen:", curBlockLen, "src:", pl.src,"outDeg",pl.deg, "oldRanklen:", len(oldRank) , "oldRank:",oldRank[pl.src])
                    newBlockRank[dest %
                                 self.block] += self.beta * oldRank[pl.src] / pl.deg
            self.extendNewRank(newBlockRank)
        self.storeOldRank(oldRank)

    @metric.printTimeElapsed
    def isConvergence(self, epsilon: float, metricFunc=metric.metric.get2Norm) -> (bool, float):
        newRank = self.loadNewRank()
        oldRank = self.loadOldRank()
        # print("new:", newRank)
        # print("old:", oldRank)
        metric = metricFunc([x[0] - x[1]
                             for x in zip(self.rank, self.oldRank)])
        if metric <= epsilon:
            return True, metric
        return False, metric

    @metric.printTimeElapsed
    def getkBest(self, k: int) -> [page]:
        '''
        top-k problem
        '''
        res = [page(i, v) for i, v in enumerate(self.rank[:k])]
        heapq.heapify(res)
        for i, v in enumerate(self.rank[k:]):
            if v < res[0].rank:
                continue
            else:
                heapq.heapreplace(res, page(i+k, v))
        res.sort(reverse=True)
        return res


def TestGetKBest():
    pr = pageRank(
        sparseMat([[0.5, 0.2, 0.1], [0.5, 0.3, 0.3], [0, 0.5, 0.6]]), 0.8)
    while(True):
        pr.iter(1)
        if pr.isConvergence(0.00001):
            break
    pages = pr.getkBest(3)
    print(pages)
    pages = pr.getkBest(2)
    print(pages)


def Test():
    TestGetKBest()


if __name__ == "__main__":
    Test()
