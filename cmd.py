import rawMatGen
import sparseMatGen
import powerIter
import time

beta = 0.8
N = 10000
block = 10
epsilon = 0.01
topK = 10


def printSuperParam(delim):
    print(delim)
    print(f"N:{N},block:{block},epsilon:{epsilon},topK:{topK},beta:{beta}")


def pageRankFromRawMat(block=2):
    rawMat = rawMatGen.rawMat(N)
    sparseMat = sparseMatGen.sparseMat(rawMat, block)
    pr = powerIter.pageRank(sparseMat, beta, block)

    cnt = 0
    loss = 0.
    beg = time.time()
    while (True):
        cnt += 1
        pr.iter(block)
        ok, loss = pr.isConvergence(epsilon)
        print(f"iter:{cnt} loss:{loss}")
        if ok:
            break

    end = time.time()

    print(f"[done] iter:{cnt} , loss={loss} , time:{end-beg}s ")
    pages = pr.getkBest(topK)
    pages.sort(reverse=True)
    printSuperParam("=*"*20)
    print(f"topK:{topK}", pages)


def pageRankDirectly(block=2):
    # rawMat = rawMatGen.rawMat(N)
    sparseMat = sparseMatGen.sparseMat(N, block)
    pr = powerIter.pageRank(sparseMat, beta, block)

    cnt = 0
    loss = 0.
    beg = time.time()
    while (True):
        cnt += 1
        pr.iter(block)
        ok, loss = pr.isConvergence(epsilon)
        print(f"iter:{cnt} loss:{loss}")
        if ok:
            break

    end = time.time()

    print(f"[done] iter:{cnt} , loss={loss} , time:{end-beg}s ")
    pages = pr.getkBest(topK)
    pages.sort(reverse=True)
    printSuperParam("=*"*20)
    print(f"topK:{topK}", pages)


pageRankDirectly(block)