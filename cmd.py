#!/usr/bin/python3
# -- coding:utf8 --
# line encoding :unix: LF
import time
import model
import util
import metric
from pyspark import SparkContext

norm = metric.metric.get1Norm
beta = 0.8
N = 100
epsilon = 0.01
topK = 10


def printSuperParam(delim=""):
    print("\033[1;31m"+delim)
    print(
        f" norm:{norm.__name__} epsilon:{epsilon} beta:{beta}")
    print(f"N:{N} topK:{topK}")
    print(delim, "\033[0m")


def update(ranklist, size, beta):
    newRank = []
    pl = ranklist[1][1]
    for dest in pl.dests:
        tempval = 1/size + beta * ranklist[1][0] / pl.deg
        newRank.append((dest, tempval))
    return newRank


def parseLine(line: str):
    nums = list(map(int, line.strip().split(" ")))
    return (nums[0], model.pageLink(nums[0], nums[1], nums[2:]))


@metric.printTimeElapsed
def pageRank():
    cnt = 0
    loss = 0.
    beg = time.time()

    sc = SparkContext("localhost", "PageRank")
    logData = sc.textFile(
        "hdfs://localhost:9000/user/hadoop/input/Data_1000000.txt")

    # matrix_rdd 形如[(i , pageLink{i,deg,dests})]
    martrix_rdd = logData.map(lambda line: parseLine(line))
    # ranklist_rdd 形如[(i , rank)]
    ranklist_rdd = sc.parallelize([(i, -999) for i in range(N)])
    for i in range(0, 10):
        cnt += 1
        ranklist_rdd = ranklist_rdd.leftOuterJoin(martrix_rdd)
        map_ranklist_rdd = ranklist_rdd.flarMap(
            lambda x: update(x, N, beta))
        ranklist_rdd = map_ranklist_rdd.reduceByKey(lambda x, y: x+y)

    end = time.time()

    print(
        f"\033[1;32m[done] iter:{cnt} , loss={loss} , time:{end-beg}s \033[0m")
    pages = ranklist_rdd.takeOrdered(topK, lambda k, v: v)
    pages = model.ToPages(pages)
    # pages = util.getKBest(topK, ranklist_rdd.collect())
    printSuperParam("=*"*20)
    print(f"topK:{topK}", pages)


if '__name__' == '__main__':
    printSuperParam("~x~ "*10)
    pageRank()
