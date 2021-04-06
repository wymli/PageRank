
import math
import time


class metric(object):
    @staticmethod
    def get1Norm(a: []):
        '''
        sum of absolute value
        '''
        return sum(map(abs, a))

    @staticmethod
    def get2Norm(a: []):
        return math.sqrt(sum(map(lambda x: x**2, a)))

    @staticmethod
    def getInfNorm(a: []):
        return max(map(abs, a))


def TestMetric():
    a = [1, 2, 3, 4, 5, 6, 7, 8, -9]
    print(metric.get1Norm(a))
    print(metric.get2Norm(a))
    print(metric.getInfNorm(a))


def printTimeElapsed(ff):
    def f(*args, **kw):
        beg = time.time()
        res = ff(*args, **kw)
        end = time.time()
        fn = ff.__name__
        print(f"[Time] function {fn: <30} \tdone, elapsed: {end-beg}s")
        return res
    return f


@printTimeElapsed
def f(a, b, c):
    pass


def TestPrintTimeElapsed():
    f(1, 2, 3)


def Test():
    TestMetric()
    TestPrintTimeElapsed()


if __name__ == "__main__":
    Test()
