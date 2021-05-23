import metric
import heapq
from model import page


@metric.printTimeElapsed
def getKBest(k: int, rankList) -> [page]:
    '''
    top-k problem
    '''
    newRank = rankList
    res = [page(i, v) for i, v in enumerate(newRank[:k])]
    heapq.heapify(res)
    for i, v in enumerate(newRank[k:]):
        if v < res[0].rank:
            continue
        else:
            heapq.heapreplace(res, page(i+k, v))
    res.sort(reverse=True)
    return res
