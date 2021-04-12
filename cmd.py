#!/usr/bin/python3
# line encoding :unix: LF
import rawMatGen
import sparseMatGen
import powerIter
import time
import metric


norm = metric.metric.get1Norm
beta = 0.8
N = 100000
rankBlock = 2
tranMatBlock = 2
epsilon = 0.01
topK = 10

# note: maybe the best practise: block=2



def getMethodStr() -> str:
    if rankBlock != 1 and tranMatBlock != 1:
        return "block-strip"
    elif rankBlock != 1 and tranMatBlock == 1:
        return "block-based"
    elif rankBlock == 1 and tranMatBlock == 1:
        return "unblock"
    else:
        raise "not supported method"


def printSuperParam(delim=""):
    print("\033[1;31m"+delim)
    print(
        f"method:{getMethodStr()} norm:{norm.__name__} epsilon:{epsilon} beta:{beta}")
    print(f"N:{N} rankBlock:{rankBlock} transferMatBlock:{tranMatBlock} topK:{topK}")
    print(delim, "\033[0m")


printSuperParam("")


def pageRankFromRawMat():
    '''
    deprecated: rawMat will cause OOM,using pageRankFromRandom instead
    '''
    rawMat = rawMatGen.rawMat(N)
    sparseMat = sparseMatGen.sparseMat(rawMat, tranMatBlock)
    pr = powerIter.pageRank(sparseMat, beta, rankBlock)

    cnt = 0
    loss = 0.
    beg = time.time()
    while (True):
        cnt += 1
        pr.iter(rankBlock)
        ok, loss = pr.isConvergence(epsilon, metric.metric.get1Norm)
        print(f"iter:{cnt} loss:{loss}")
        if ok:
            break

    end = time.time()

    print(f"[done] iter:{cnt} , loss={loss} , time:{end-beg}s ")
    pages = pr.getkBest(topK)
    pages.sort(reverse=True)
    printSuperParam("=*"*20)
    print(f"topK:{topK}", pages)


@metric.printTimeElapsed
def pageRankFromRandom():
    sparseMat = sparseMatGen.sparseMat(N, tranMatBlock)
    pr = powerIter.pageRank(sparseMat, beta, rankBlock)

    cnt = 0
    loss = 0.
    beg = time.time()

    while (True):
        cnt += 1
        # use rankBlock to iter, if rankBlock != tranMatBlock, it should be a block-based powerIter
        pr.iter(rankBlock)
        ok, loss = pr.isConvergence(epsilon, norm)
        print(f"\033[1;36miter:{cnt} loss:{loss}\033[0m")
        if ok:
            break

    end = time.time()

    print(
        f"\033[1;32m[done] iter:{cnt} , loss={loss} , time:{end-beg}s \033[0m")
    pages = pr.getkBest(topK)
    printSuperParam("=*"*20)
    print(f"topK:{topK}", pages)


pageRankFromRandom()
