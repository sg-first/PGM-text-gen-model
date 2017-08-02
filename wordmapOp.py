import help
import parameter
import node
import lang

def genWordMap(wordmap,sen):
    wnlist=[]
    # 先把word都转换成node
    for word in sen:
        if lang.isStopWord(word):
            wnlist.append(None) # 停用词
        else:
            wnlist.append(node.findornew(wordmap,word))
    # 然后进行接边的连接
    for n1 in range(len(wnlist)):
        if wnlist[n1] is None: # 本身就是停用词，跳过
            continue
        # 特殊位置检测
        if n1 == 0: # 第一位，不连接前向接边
            wnlist[n1].firstp += 1
        else:
            wnlist[n1].autoChangeFrontNode(wnlist[n1 - 1], help.getindex(wnlist, n1 - 2), sen[n1 - 1], 1)
        if n1!=len(sen)-1: # 不是最后一位，连接后向接边
            wnlist[n1].autoChangeBehindNode(wnlist[n1 + 1], help.getindex(wnlist, n1 + 2), sen[n1 + 1], 1)

def caluwordCount(n,senllist):
    wordCount = 0
    for senlist in senllist:
        for sen in senlist:
            wordCount += help.caluCount(sen, n.word)
    return wordCount

def normalizedWeight(wordmap,senllist): # 归一化句首概率和边权
    senCount=0
    for senlist in senllist:
        senCount += len(senlist)

    for n in wordmap:
        # 遍历wordmap，给所有node添加同义边
        for n2 in wordmap:
            if n.word==n2.word:
                continue # 不搞自己
            if lang.isSynonyms(n.word,n2.word):
                n.addSynonyms(n2)
        # 正式的归一化过程
        n.firstp /= senCount  # 句首次数归一化（使用等价贝叶斯后这也是真归一化）
        n.wordCount=caluwordCount(n,senllist) # 首先计算该词在整个训练文本中出现的次数（由于停用词不会在wordmap中出现，所以数量上也不会把停用词算在内）
        # 边权归一化
        for nunion in n.behindNode:
            nunion["count"]=nunion["P"]
            nunion["P"] = help.limitDigits(nunion["P"] / n.wordCount*parameter.stackWeights) #使用等价贝叶斯后，P仅作为边权，而句子概率使用count计算
            for sw in nunion["stopList"]:
                sw.p/=n.wordCount #停用词依然真归一化
        for nunion in n.frontNode:
            nunion["count"] = nunion["P"]
            nunion["P"] = help.limitDigits(nunion["P"] / n.wordCount*parameter.stackWeights)
            for sw in nunion["stopList"]:
                sw.p/=n.wordCount

def nodeConduct(wnode,activateSignal,formDelta):
    if activateSignal<parameter.activeThreshold:
        return
    # 条件符合，进行传导
    wnode.activation+=activateSignal #乘边权的过程放在递归前，如下
    if not wnode.caluForm=='':
        wnode.caluForm+='+'
    wnode.caluForm+=formDelta
    for nunion in wnode.behindNode:
        if not nunion["isPass"]:
            nunion["isPass"]=True
            # 这里是一种优化，严格来说应该是在从后向边激活后，禁止被激活词从前向边重复激活该词。但这样需要在此反复遍历寻找该词在behindNode中的位置。因此这里禁传自己，然后被激活词前向回传
            # 一次，也同样禁传自己，二者就不会重复传递
            newformDelta = wnode.caluForm + '*' + str(nunion["P"])
            nodeConduct(nunion["node"], activateSignal * nunion["P"], newformDelta)
    for nunion in wnode.frontNode:
        if not nunion["isPass"]:
            nunion["isPass"]=True
            newformDelta = wnode.caluForm + '*' + str(nunion["P"])
            nodeConduct(nunion["node"], activateSignal * nunion["P"], newformDelta)
    for pair in wnode.synonymNode:
        if not pair["isPass"]:
            pair["isPass"]=True
            nodeConduct(pair["node"],activateSignal,wnode.caluForm) #同义边传导无衰减

def getsenpair(wordmap):
    senpair = []  # [{sen,P}]
    for n in wordmap:
        if n.activation>parameter.minactive and n.firstp>0: # 从每个备选词出发试图产生句子
            sen = [] # 从n出发试图产生的句子
            # 产生句首停用词
            stopword=node.genStopWord(n.frontStop)
            if not stopword is None:
                sen.append(stopword)
            nextword(n,sen,n.firstp,senpair)
    return senpair

def nextword(n,sen,p,senpair):
    isEnd=True #是否到达本次递归结束时（找不到下一个词）

    for nunion in n.behindNode:
        newp=p*lang.equBayes(n.wordCount, nunion["count"])
        if n.activation>parameter.minactive and newp>parameter.minp:
            isEnd=False #能找到一个就不结束
            #产生过渡停用词
            stopword=node.genStopWord(nunion["stopList"])
            if not stopword is None:
                sen.append(stopword)
            sen.append(n)
            nextword(nunion["node"],sen,newp,senpair)
            # 这里无限扩展应该并没有问题，因为训练可以使得初激活值调整到生成正常长度的合理句子

    if isEnd: #一个都找不到，即结束
        # 产生句尾停用词
        stopword=node.genStopWord(n.behindStop)
        if not stopword is None:
            sen.append(stopword)
        senpair.append({"sen":sen,"P":p})

def getmaxsen(senpair):
    return help.getmax(senpair,"sen")

def clearActivation(wordmap):
    for n in wordmap:
        n.activation=0
        n.caluForm=''
        for nunion in n.behindNode:
            nunion["isPass"]=False
        for nunion in n.frontNode:
            nunion["isPass"]=False
        for pair in n.synonymNode:
            pair["isPass"]=False