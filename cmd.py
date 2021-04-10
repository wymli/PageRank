#!/usr/bin/python3
# line encoding :unix: LF
import rawMatGen
import sparseMatGen
import powerIter
import time
import metric

version = "block-strip"
norm = metric.metric.get1Norm
beta = 0.8
N = 100000
block = 2
epsilon = 0.01
topK = 10

# note: maybe we will iter "N*N*outDeg / block" times when we make block-strip sparseMat
# note: the best practise: block=2


def printSuperParam(delim):
    print("\033[1;31m"+delim)
    print(
        f"version:{version} norm:{norm.__name__} N:{N} block:{block} epsilon:{epsilon} beta:{beta} topK:{topK}")
    print(delim, "\033[0m")


def pageRankFromRawMat(block=2):
    '''
    deprecated: rawMat will cause OOM,using pageRankFromRandom instead
    '''
    rawMat = rawMatGen.rawMat(N)
    sparseMat = sparseMatGen.sparseMat(rawMat, block)
    pr = powerIter.pageRank(sparseMat, beta, block)

    cnt = 0
    loss = 0.
    beg = time.time()
    while (True):
        cnt += 1
        pr.iter(block)
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
def pageRankFromRandom(block=2):
    # rawMat = rawMatGen.rawMat(N)
    sparseMat = sparseMatGen.sparseMat(N, block)
    pr = powerIter.pageRank(sparseMat, beta, block)

    cnt = 0
    loss = 0.
    beg = time.time()

    while (True):
        cnt += 1
        pr.iter(block)
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


pageRankFromRandom(block)
