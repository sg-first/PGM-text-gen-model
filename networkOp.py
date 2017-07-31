import lang
import parentNode
import node
import parameter
import help
import math
import copy
import random

def genBlock(wordmap,sen,allpnode):
    wnodeList=node.charFindNodeList(wordmap,sen)
    sum=lang.summary(sen)
    block=[]

    for w1 in sum:
        nw1 = parentNode.findornew(allpnode,w1)
        block.append(nw1)
        # 产生全连接子节点
        for wnode in wnodeList:
            if parameter.radomWeight:
                nw1.addsonNode(wnode,random.randint(1,300)) #针对于未使用贝叶斯的情况，先调300
            else:
                nw1.addsonNode(wnode,1)

        return parentNode.pnBlock(block,sen)

def genNetwork(network,wordmap,allpnode,senlist):
    blist=[]
    # 先用senlist生成摘要块序列
    for sen in senlist:
        blist.append(genBlock(wordmap,sen,allpnode))
    # 然后进行接边的连接
    for b1 in range(len(blist)):
        # 特殊位置检测
        if b1 == 1:  # 第一位，不连接前向接边
            blist[b1].firstp += 1
        else:
            blist[b1].changeBehindNode(blist[b1+1],1)
        if b1 != len(senlist) - 1:  # 是最后一位，不连接后向接边
            blist[b1].changeFrontNode(blist[b1-1],1)
        network.append(blist[b1])

def caluSimCount(sen,network):
    count=0
    for b in network:
        if lang.isSim(sen,b.sen):
            count+=1
    return count

def normalizedWeight(network,senllist):
    chapterCount=len(senllist)
    for b in network:
        # 遍历network，将所有相似块的接边合并
        for b2 in network:
            if b.sen==b2.sen:
                continue # 不搞自己
            if lang.isSim(b.sen, b2.sen):
                for nunion in b.behindNode: # 把b的接边中的每个元素都拿去与b2的合并
                    b2.dirChangeBehindNode(nunion["pnBlock"].sen,nunion["pnBlock"],nunion["P"])
                b.behindNode=copy.deepcopy(b2.behindNode) # 再把b2的拿给b
                for nunion in b.frontNode: # 把b的接边中的每个元素都拿去与b2的合并
                    b2.dirChangeFrontNode(nunion["pnBlock"].sen,nunion["pnBlock"],nunion["P"])
                b.frontNode=copy.deepcopy(b2.frontNode) # 再把b2的拿给b
        # 正式的归一化过程
        b.firstp/=chapterCount  # 句首次数归一化
        simCount=caluSimCount(b.sen,network) # 首先计算该句在整个训练文本中出现的次数
        # 边权归一化
        for sunion in b.behindNode:
            sunion["P"]/=simCount
        for sunion in b.frontNode:
            sunion["P"]/=simCount

def blockConduct(b,activateSignal):
    if activateSignal < parameter.activeThresholdB:
        return
    # 条件符合，进行传导
    b.activation += activateSignal  # 乘边权的过程放在递归前，如下
    for nunion in b.behindNode:
        if not nunion["isPass"]:
            nunion["isPass"] = True
            # 这里是一种优化，严格来说应该是在从后向边激活后，禁止被激活词从前向边重复激活该词。但这样需要在此反复遍历寻找该词在behindNode中的位置。因此这里禁传自己，然后被激活词前向回传
            # 一次，也同样禁传自己，二者就不会重复传递
            blockConduct(nunion["node"], activateSignal * nunion["P"])
    for nunion in b.frontNode:
        if not nunion["isPass"]:
            nunion["isPass"] = True
            blockConduct(nunion["node"], activateSignal * nunion["P"])

def getblpair(network): # 生成概率大的块序列
    blpair=[] # [{blockList,P}]
    for b in network:
        if b.activation > parameter.minactiveB and b.firstp > 0:  # 从每个备选块出发试图产生块序列
            blist=[] # 从b出发试图产生的块序列
            nextblock(b, blist, math.log2(b.firstp), blpair)
    return blpair

def nextblock(b,blist,p,blpair):
    isEnd = True  # 是否到达本次递归结束时（找不到下一个块）

    for nunion in b.behindNode:
        newp=p+math.log2(nunion["P"])
        if b.activation > parameter.minactiveB and newp>parameter.minpB:
            isEnd = False  # 能找到一个就不结束
            blist.append(b)
            nextblock(nunion["node"], blist, newp, blpair)

    if isEnd: #一个都找不到，即结束
        p*=len(blist) #对概率进行取均值平滑
        blpair.append({"blist":blist, "P":p})

def getmaxblist(blpair):
    return help.getmax(blpair,"blist")

# 注意，blist完全可以通过network中的元素自定义而不是通过传导生成
def genChapter(blist,wordmap):
    rsen=""
    for b in blist:
        sen=b.activeBlock(wordmap)
        rsen+=help.listToStr(sen)+"。"
    return rsen

def clearActivation(network):
    for b in network:
        b.activation=0
        for nunion in b.behindNode:
            nunion["isPass"]=False
        for nunion in b.frontNode:
            nunion["isPass"]=False
