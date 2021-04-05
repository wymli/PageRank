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

目前，我们首先生成了原始的未分块的sparseMat，然后将其转换成分块的sparseMat，这需要至少N^2/block的遍历次数（这里block指一个block所含的page数) ，依旧缓慢，等待优化

## 幂迭代

迭代速度是快速的,且普遍的,迭代次数为1
```sh
[decorate] function GenBlockPageLinks   done, elapsed: 292.35559582710266s
[decorate] function iterBlock   done, elapsed: 1.3519837856292725s
[decorate] function iter        done, elapsed: 1.3529930114746094s
[decorate] function isConvergence       done, elapsed: 0.0529789924621582s
iter:1 loss:0.0008151764340924569
[done] iter:1 , loss=0.0008151764340924569 , time:1.4059720039367676s 
[decorate] function getkBest    done, elapsed: 0.020017147064208984s
=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
N:100000,block:100,epsilon:0.01,topK:10,beta:0.8
=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
topK:10 [{95308,2.338812298812299e-05}, {69491,2.3256454656454662e-05}, {81164,2.2819513819513822e-05}, {19127,2.255437895437896e-05}, {8824,2.2483938283938286e-05}, {47170,2.246568986568987e-05}, {16190,2.2390564990564995e-05}, {48997,2.1872416472416473e-05}, {10924,2.1771228771228773e-05}, {14275,2.165845265845266e-05}]
[decorate] function pageRankDirectly    done, elapsed: 294.7816412448883s
```

## 耗时
程序的耗时主要在生成分块的稀疏矩阵上,
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