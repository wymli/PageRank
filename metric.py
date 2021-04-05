
import math

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


def Test():
    TestMetric()


if __name__ == "__main__":
    Test()
