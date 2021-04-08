import rawMatGen
import sparseMatGen
import powerIter
import time
import metric

beta = 0.8
N = 100000
block = 2
epsilon = 0.01
topK = 10
# note: maybe we will iter "N*N*outDeg / block" times when we make block-strip sparseMat 
# note: the best practise: block=2

def printSuperParam(delim):
    print(delim)
    print(f"N:{N},block:{block},epsilon:{epsilon},topK:{topK},beta:{beta}")
    print(delim)


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
        ok, loss = pr.isConvergence(epsilon,metric.metric.get1Norm)
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
        ok, loss = pr.isConvergence(epsilon,metric.metric.get1Norm)
        print(f"iter:{cnt} loss:{loss}")
        if ok:
            break

    end = time.time()

    print(f"[done] iter:{cnt} , loss={loss} , time:{end-beg}s ")
    pages = pr.getkBest(topK)
    printSuperParam("=*"*20)
    print(f"topK:{topK}", pages)


pageRankFromRandom(block)