
import random
import time
from ITransferMat import ITransferMat


def getRandOutDeg(beg=6, end=15) -> int:
    '''
    [beg,end]
    '''
    # note: there is no need to set random.seed to time_nano
    return random.randint(beg, end)


def TestGetRandOutDeg():
    print("%s(6,15)" % TestGetRandOutDeg.__name__, getRandOutDeg(6, 15))


def getRandOutPageIdx(outDegree: int, N: int):
    '''
    select outDegree rows out of N rows
    '''
    return random.sample(range(N), outDegree)


def TestGetRandOutPageIdx():
    print("%s(4,10)" % TestGetRandOutPageIdx.__name__, getRandOutPageIdx(4, 10))


def getOneCol(N: int) -> [int]:
    k = getRandOutDeg(6, 15)
    idxs = getRandOutPageIdx(k, N)
    col = [1./k if i in idxs else 0 for i in range(N)]
    return col


def TestGetOneCol():
    print("%s(10)" % TestGetOneCol.__name__, getOneCol(10))


def transpose(a: [[]]) -> [[]]:
    return list(map(list, zip(*a)))


def TestTranspose():
    a = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    print("%s" % TestTranspose.__name__, a, transpose(a))


def setValue(data, idxs, value):
    for i in range(len(data)):
        data[i] = value if i in idxs else 0


def sumNonZero(a: []) -> int:
    '''
    typically, it will be used to calculate the outDegree of one col
    '''
    return sum(map(lambda x: 1 if x != 0 else 0, a))

def TestSumNonZero():
    res = sumNonZero([1,2,3,0,2,2,0,-1,9.4,1.2,0])
    if  res != 8:
        print(f"test fail => get:{res} , want:8")
    else:
        print(f"test success => get:{res} , want:8")


class rawMat(ITransferMat):
    def __init__(self, N: int, degRange: [] = [6, 15]):
        '''
        deprecated: we will OOM if N = 10K ,we should generate sparseMat directly
        '''
        self.mat, self.degs = self.getMatrix(N, degRange[0], degRange[1])

    def size(self):
        return len(self.mat)

    def __getitem__(self, i):
        return self.mat[i]

    def __str__(self):
        return f"rawMat{{{self.mat}}}"

    __repr__ = __str__

    @staticmethod
    def getMatrix(N: int, loDeg=6, hiDeg=15) -> ([[]], []):
        '''
        N rows, N cols
        deprecated: we will OOM if N = 10K ,we should generate sparseMat directly
        '''
        # note: u can't generate mat using [[0]*N]*N,which is using ref
        mat = [[0 for _ in range(N)] for _ in range(N)]
        degs = [0 for _ in range(N)]
        for i in range(N):
            deg = getRandOutDeg(loDeg, hiDeg)
            degs[i] = deg
            idxs = getRandOutPageIdx(deg, N)
            # print(deg, idxs)
            setValue(mat[i], idxs, 1./deg)
            # print("mat[i]:",mat[i])
        # print("mat", mat)
        return transpose(mat), degs


def TestRawMat():
    mat = rawMat(5, [1, 5])
    print("%s" % TestRawMat.__name__, mat)
    print(mat[0])
    print(mat[0][0])


def Test():
    # TestGetRandOutDeg()
    # TestGetRandOutPageIdx()
    # TestGetOneCol()
    # TestTranspose()
    # TestRawMat()
    TestSumNonZero()
    pass


if __name__ == "__main__":
    Test()
