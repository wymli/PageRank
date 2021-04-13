from sparseMatGen import sparseMat
from ITransferMat import ITransferMat
import metric
import heapq
import json
from os import path
import os

mock = False


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
    def __init__(self, transferMat: ITransferMat, beta: float, block: int = 1, storeDir: str = "./tmp"):
        '''
        1-beta : the rate of tp;\n
        block: the number of pages in one block;\n
        self.rank will be stored in "newRank"\n
        self.oldRank will be stored in "oldRank"\n
        '''
        if not path.isdir(storeDir):
            os.makedirs(storeDir)
        self.newFileName = path.join(storeDir, "newRank")
        self.oldFileName = path.join(storeDir, "oldRank")
        self.size = transferMat.size()
        self.storeNewRank([1./self.size for _ in range(self.size)])
        self.storeOldRank([-999 for _ in range(self.size)])
        self.mat = transferMat
        self.beta = beta
        self.block = block
        self.tranMatBlock = transferMat.block
        self.preVal = (1.-self.beta)/self.size

    def loadRank(self, type: str) -> []:
        '''
        we will load data from storeDir
        if block == 1 ,we won't block i.e. return a origin rank list,otherwise return a block-based rank list
        \ntodo: we should change block = 1 to block=size,i.e. if block == size ,we won't block
        \n
        todo: write a decoder generater,which yield a block from file each iter.
        we must implement it ourselves, because we only want to read one block into memory one time
        '''
        if type == "new":
            if mock:
                return self.rank.copy()
            return pageRank.fileTolist(self.newFileName)
        elif type == "old":
            if mock:
                return self.oldRank.copy()
            return pageRank.fileTolist(self.oldFileName)
        else:
            raise "type not inplemented"

    def loadNewRank(self) -> []:
        '''
        default: block=1, unblock, return the whole rank
        '''
        return self.loadRank("new")

    def loadOldRank(self) -> []:
        '''
        default: block=1, unblock, return the whole rank
        '''
        return self.loadRank("old")

    @staticmethod
    def listToFile(rank: [], filename: str):
        with open(filename, "w") as f:
            for r in rank:
                f.write(str(r)+"\n")

    @staticmethod
    def fileTolist(filename: str):
        with open(filename, "r")as f:
            res = []
            for line in f:
                res.append(float(line.strip("\n")))
        return res

    def storeRank(self, rank: [], type: str):
        '''
        we will store data to storeDir\n
        todo: add a encoder ,write the encoded str/binary to file
        '''
        if type == "new":
            self.rank = rank
            pageRank.listToFile(rank, self.newFileName)
            return
        elif type == "old":
            self.oldRank = rank
            pageRank.listToFile(rank, self.oldFileName)
            return
        else:
            raise "type not inplemented"

    def storeNewRank(self, rank: []):
        self.storeRank(rank, "new")

    def storeOldRank(self, rank: []):
        self.storeRank(rank, "old")

    def extendNewRank(self, rank: [], fp):
        '''
        only append it to "new",typically it will append one block rank to rankFile
        \n
        todo: add a encoder ,append the encoded str/binary to the file\n
        if you use json, you should remove the last "}" in the file ,
        and then append this encoded str of the block,and then add "}" to make a close
        '''
        self.rank.extend(rank)
        # append
        for r in rank:
            fp.write(str(r)+"\n")
        return

    def expireNewRank(self):
        '''
        when we run a new iter,we will call expire\n
        typically,the original newRank should be changed to oldRank,
        so we will rename newRank to oldRank,and make newRank empty
        '''
        self.oldRank = self.rank.copy()
        self.rank = []
        try:
            os.rename(self.newFileName, self.oldFileName)
        except Exception:
            os.remove(self.oldFileName)
            os.rename(self.newFileName, self.oldFileName)

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
        self.expireNewRank()
        oldRank = self.loadOldRank()

        for i in range(self.size):
            pl = self.mat.getPageLink(i)
            for dest in pl.dests:
                newRank[dest] += self.beta * oldRank[pl.src] / pl.deg

        self.storeNewRank(newRank)

    @metric.printTimeElapsed
    def iterBlock(self):
        '''
        this is a kind of block-based or block-strip pagerank
        '''
        self.expireNewRank()
        oldRank = self.loadOldRank()
        fp = open(self.newFileName, "w")

        n = (self.size+self.block-1) // self.block  # ceil(rawMat / block)
        for i in range(n):
            curBlockLen = min((i+1)*self.block, self.size) - i*self.block
            newBlockRank = [self.preVal for _ in range(curBlockLen)]
            blockPL = self.mat.getBlockPageLink(i)
            for pl in blockPL:
                for dest in pl.dests:
                    # print("dest:", dest, "block:", self.block,
                    #       "curBlocklen:", curBlockLen, "src:", pl.src,"outDeg",pl.deg, "oldRanklen:", len(oldRank) , "oldRank:",oldRank[pl.src])
                    newBlockRank[dest %
                                 self.block] += self.beta * oldRank[pl.src] / pl.deg
            self.extendNewRank(newBlockRank, fp)
        fp.close()
        # self.storeOldRank(oldRank)

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
