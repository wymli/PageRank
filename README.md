# PageRank

## 类型定义

```go
type rawMat struct{
    mat [][]float
}

type pageLink struct{
    src int
    deg int
    dests []int
}

type blockPageLink struct{
    pageLinks []pageLink
}

type sparseMat struct{
    pageLinks []blockPageLink
}

type pageRank struct{
    transferMat sparseMat
    oldRank []float
    newRank []float
}
```

```mermaid
graph LR;
x(random)-->a("rawMat([[float]])")-->b("sparseMat([pageLink])")-->c(pageRank)-->|"iter()"|c
c -->|"isConvergence()"| c
c -->|"getkBest()"| c
```

## 数据生成

在实际生成数据时，不适用rawMat，而是直接在sparseMat中一边生成列数据，一边转成pageLink，否则巨大的rawMat会导致OOM，即使我们有足够的内存，我们在遍历rawMat生成sparseMat的时候，也会需要至少N^2的遍历次数，极其缓慢

一种朴素的想法是首先生成原始的未分块的sparseMat，然后将其转换成分块的sparseMat，这需要至少N^2*outDegree/block的遍历次数（这里block指一个block所含的page数),在实践上,这很慢

目前我们采用直接生成分块的sparseMat,速度上大幅提升

## 幂迭代
迭代速度是快速的,且普遍为1.4s左右,迭代次数为1
```sh
[Time] function GenBlockPageLinks               done, elapsed: 11.590656995773315s
[Time] function iterBlock                       done, elapsed: 1.544142246246338s
[Time] function iter                            done, elapsed: 1.545184850692749s
[Time] function isConvergence                   done, elapsed: 0.0509946346282959s
iter:1 loss:0.000812115524604311
[done] iter:1 , loss=0.000812115524604311 , time:1.6011526584625244s
[Time] function getkBest                        done, elapsed: 0.025041818618774414s
=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
N:100000,block:2,epsilon:0.01,topK:10,beta:0.8
=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
topK:10 [{85809,2.2703585303585302e-05}, {16306,2.2444422244422245e-05}, {85884,2.1527938727938727e-05}, {62114,2.149019869019869e-05}, {49771,2.1474614274614276e-05}, {88772,2.1457431457431456e-05}, {41516,2.1288089688089685e-05}, {8502,2.124693084693085e-05}, {33764,2.1246153[Time] function pageRankFromRandom              done, elapsed: 14.226988077163696s
```

## 耗时
程序的耗时主要在生成分块的稀疏矩阵上,
当N=100K,block=2时,生成分块稀疏矩阵的时间为11s左右,而迭代时间仅为1.4s左右
当N=100K,block=10时,生成分块稀疏矩阵的时间为31s左右,而迭代时间仅为1.4s左右
当N=100K,block=100时,生成分块稀疏矩阵的时间为292s左右,而迭代时间仅为1.4s左右
当N=100K,block=1000时,生成分块稀疏矩阵的时间为2815s左右,而迭代时间仅为1.4s左右


## 序列化

在分块的设计中，我们应该一次从文件中读取一块，目前用内存模拟,一次读取内存的一块

在序列化设计中，要考虑block是不定长的，dests是不定长的，这两个都要在前面加长度字段

## Metric

集成了常见的三种范数

```python
class metric(object):
    @staticmethod
    def get1Norm(a: []):
        return sum(map(abs, a))

    @staticmethod
    def get2Norm(a: []):
        return math.sqrt(sum(map(lambda x: x**2, a)))

    @staticmethod
    def getInfNorm(a: []):
        return max(map(abs, a))
```

## TopK problem
题目要求输出 PageRank值最大的10个网页的编号与对应PageRank值,这是典型的topk问题,我们使用一个简单的小顶堆完成近似O(NlogK)的检索

## TODO
- 判断block=1 改为 判断block=size,作为不分块的判断条件,以此兼容non-block alg.,block-based alg.,block-strip alg.