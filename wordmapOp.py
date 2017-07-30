import help
import parameter
import node
import lang
import math

def genWordMap(wordmap,sen):
    wnlist=[]
    # 先把char都转换成node
    for char in sen:
        if lang.isStopWord(char):
            wnlist.append(None) #停用词
        else:
            wnlist.append(node.findornew(wordmap,char))
    # 然后进行接边的连接
    for n1 in range(len(wnlist)):
        if lang.isStopWord(sen[w1]): # 本身就是停用词，跳过
            continue
        nw1=node.findornew(wordmap,sen[w1])
        #特殊位置检测
        if w1 == 1: #第一位，不连接前向接边
            nw1.firstp += 1
        else:
            nw1.autoChangeBehindNode(sen[w1+1],help.index(sen,w1+2),1)
        if w1!=len(sen)-1: #是最后一位，不连接后向接边
            nw1.autoChangeFrontNode(sen[w1-1],help.index(sen,w1-2),1)

def caluwordCount(n,senllist):
    wordCount = 0
    for senlist in senllist:
        for sen in senlist:
            wordCount += help.caluCount(sen, n.char)
    return wordCount

def normalizedWeight(wordmap,senllist): # 归一化句首概率和边权
    senCount=0
    for senlist in senllist:
        senCount += len(senlist)

    for n in wordmap:
        # 遍历wordmap，给所有node添加同义边
        for n2 in wordmap:
            if n.char==n2.char:
                continue # 不搞自己
            if lang.isSynonyms(n.char,n2.char):
                n.addSynonyms(n2)
        # 正式的归一化过程
        n.firstp /= senCount  # 句首次数归一化
        wordCount=caluwordCount(n,senllist) # 首先计算该词在整个训练文本中出现的次数（由于停用词不会在wordmap中出现，所以数量上也不会把停用词算在内）
        # 边权归一化
        for nunion in n.behindNode:
            nunion["P"]/=wordCount
            for sw in nunion["stopList"]:
                sw.p/=wordCount
        for nunion in n.frontNode:
            nunion["P"] /= wordCount
            for sw in nunion["stopList"]:
                sw.p/=wordCount
    
def nodeConduct(wnode,activateSignal):
    if activateSignal<parameter.activeThreshold:
        return
    # 条件符合，进行传导
    wnode.activation+=activateSignal #乘边权的过程放在递归前，如下
    for nunion in wnode.behindNode:
        if not nunion["isPass"]:
            nunion["isPass"]=True
            #这里是一种优化，严格来说应该是在从后向边激活后，禁止被激活词从前向边重复激活该词。但这样需要在此反复遍历寻找该词在behindNode中的位置。因此这里禁传自己，然后被激活词前向回传
            #一次，也同样禁传自己，二者就不会重复传递
            nodeConduct(nunion["node"],activateSignal*nunion["P"])
    for nunion in wnode.frontNode:
        if not nunion["isPass"]:
            nunion["isPass"]=True
            nodeConduct(nunion["node"],activateSignal*nunion["P"])
    for pair in wnode.synonymNode:
        if not pair["isPass"]:
            pair["isPass"]=True
            nodeConduct(pair["node"],activateSignal) #同义边传导无衰减

def getsenpair(wordmap):
    senpair = []  # [{sen,P}]
    for n in wordmap:
        if n.activation>parameter.minactive and n.firstp>0: # 从每个备选词出发试图产生句子
            sen = [] # 从n出发试图产生的句子
            # 产生句首停用词
            stopword=node.genStopWord(n.frontStop)
            if not stopword is None:
                sen.append(stopword)
            nextword(n,sen,math.log2(n.firstp),senpair)
    return senpair

def nextword(n,sen,p,senpair):
    isEnd=True #是否到达本次递归结束时（找不到下一个词）

    for nunion in n.behindNode:
        newp=p+math.log2(nunion["P"])
        if n.activation>parameter.minactive and newp>parameter.minp:
            isEnd=False #能找到一个就不结束
            #产生过渡停用词
            stopword=node.genStopWord(nunion["stopList"])
            if not stopword is None:
                sen.append(stopword)
            sen.append(n)
            nextword(nunion["node"],sen,newp,senpair)
            #这里无限扩展应该并没有问题，因为训练可以使得初激活值调整到生成正常长度的合理句子

    if isEnd: #一个都找不到，即结束
        #产生句尾停用词
        stopword=node.genStopWord(n.behindStop)
        if not stopword is None:
            sen.append(stopword)
            senpair.append({"sen":sen,"P":p})

def getmaxsen(senpair):
    maxelm={"sen":None,"P":0}
    for i in senpair:
        if i["P"]>maxelm["P"]:
            maxelm=i
    return maxelm["sen"]

def clearActivation(wordmap):
    for n in wordmap:
        n.activation=0
        for nunion in n.behindNode:
            nunion["isPass"]=False
        for nunion in n.frontNode:
            nunion["isPass"]=False
        for pair in n.synonymNode:
            pair["isPass"]=False