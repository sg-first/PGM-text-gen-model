import help
import parameter
import node
import lang
import copy

def genWordMap(wordmap,sen):
    wnlist=[]
    newsen=[]
    # 先把word都转换成node
    for word in sen:
        if lang.isStopWord(word):
            if len(wnlist) == 0 or not wnlist[len(wnlist)-1] is None:
                wnlist.append(None) # 停用词
                newsen.append(word)
            else:
                newsen[len(wnlist)-1]+=word
        else:
            wnlist.append(node.findornew(wordmap,word))
            newsen.append(word)
    # 然后进行接边的连接
    for n1 in range(len(wnlist)):
        if wnlist[n1] is None: # 本身就是停用词，跳过
            continue
        # 特殊位置检测
        if n1 == 0: # 第一位，不连接前向接边
            wnlist[n1].firstp += 1
        else:
            wnlist[n1].autoChangeFrontNode(wnlist[n1 - 1], help.getByIndex(wnlist, n1 - 2), newsen[n1 - 1], 1)
        if n1 == 1 and (wnlist[0] is None): # 补充句首为停用词firstp调整的情况
            wnlist[n1].firstp += 1
        if n1!=len(newsen)-1: # 不是最后一位，连接后向接边
            wnlist[n1].autoChangeBehindNode(wnlist[n1 + 1], help.getByIndex(wnlist, n1 + 2), newsen[n1 + 1], 1)

def caluwordCount(n,senllist):
    wordCount = 0
    for senlist in senllist:
        for sen in senlist:
            wordCount += help.caluCount(sen, n.word)
    return wordCount

def caluAverageFirstp(senllist):
    senCount=0
    wordCount=0
    for senlist in senllist:
        senCount+=len(senlist)
        for sen in senlist:
            wordCount+=len(sen)
    return senCount/wordCount

def normalizedWeight(wordmap,senllist): # 归一化句首概率和边权
    averageFirstp=caluAverageFirstp(senllist)
    for n in wordmap:
        # 遍历wordmap，给所有node添加同义边
        for n2 in wordmap:
            if n.word==n2.word:
                continue # 不搞自己
            if lang.isSynonyms(n.word,n2.word):
                n.addSynonyms(n2)
        # 正式的归一化过程
        n.wordCount=caluwordCount(n,senllist) # 首先计算该词在整个训练文本中出现的次数（由于停用词不会在wordmap中出现，所以数量上也不会把停用词算在内）
        # 句首次数归一化（使用等价贝叶斯）
        n.firstp /= n.wordCount
        n.firstp /= averageFirstp
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
    if len(wnode.caluForm)!=0 and len(formDelta)==1 and node.getLastForm(wnode.caluForm)['variable']==formDelta[0]['variable']:
        node.getLastForm(wnode.caluForm)['coefficient']+=formDelta[0]['coefficient']
    else:
        wnode.caluForm += formDelta

    for nunion in wnode.behindNode:
        if not nunion["isPass"]:
            nunion["isPass"]=True
            # 这里是一种优化，严格来说应该是在从后向边激活后，禁止被激活词从前向边重复激活该词。但这样需要在此反复遍历寻找该词在behindNode中的位置。因此这里禁传自己，然后被激活词前向回传
            # 一次，也同样禁传自己，二者就不会重复传递
            newcaluForm=copy.deepcopy(wnode.caluForm)
            node.getLastForm(newcaluForm)['coefficient'] *= nunion["P"]
            nodeConduct(nunion["node"], activateSignal * nunion["P"], newcaluForm)
    for nunion in wnode.frontNode:
        if not nunion["isPass"]:
            nunion["isPass"]=True
            newcaluForm=wnode.caluForm[:]
            node.getLastForm(newcaluForm)['coefficient'] *= nunion["P"]
            nodeConduct(nunion["node"], activateSignal * nunion["P"], newcaluForm)
    for pair in wnode.synonymNode:
        if not pair["isPass"]:
            pair["isPass"]=True
            nodeConduct(pair["node"],activateSignal,wnode.caluForm) #同义边传导无衰减

def caluAverageActivation(wordmap):
    total=0
    for n in wordmap:
        total+=n.activation
    global averageActivation
    averageActivation=total/len(wordmap)

def caluRelativeP(activation):
    global averageActivation
    return activation/averageActivation

def getsenpair(wordmap):
    caluAverageActivation(wordmap)
    senpair = []  # [{sen,P}]
    for n in wordmap:
        if n.activation>parameter.minactive and n.firstp>0: # 从每个备选词出发试图产生句子
            sen = [] # 从n出发试图产生的句子
            # 产生句首停用词
            stopword=node.genStopWord(n.frontStop)
            if not stopword is None:
                sen.append(stopword)
            nextword(n,sen,n.firstp*caluRelativeP(n.activation),senpair) # 传过去的n是已经确定要添加的
    return senpair

def nextword(n,sen,p,senpair):
    sen.append(n.word)
    isEnd=True # 是否到达本次递归结束时（找不到下一个词）

    if (not len(sen)>parameter.maxLength) and (not lang.isRepeat(sen)) and (not (len(sen)>parameter.topicTolerance and p<parameter.minp)):
        for nunion in n.behindNode:
            if nunion["node"].activation>parameter.minactive:
                isEnd=False #能找到一个就不结束
                newp = p * lang.equBayes(nunion["node"].wordCount, nunion["count"]) * caluRelativeP(nunion["node"].activation)
                newsen=sen[:]
                # 产生过渡停用词
                stopword=node.genStopWord(nunion["stopList"])
                if not stopword is None:
                    newsen.append(stopword)
                nextword(nunion["node"],newsen,newp,senpair)

    if isEnd: #一个都找不到，即结束
        if p>=parameter.minp:
            # 产生句尾停用词
            stopword=node.genStopWord(n.behindStop)
            if not stopword is None:
                sen.append(stopword)
            senpair.append({"sen":sen,"P":p})

def getmaxsen(senpair):
    return help.getmax(senpair,"sen")

def clearActivation(wordmap):
    global averageActivation
    averageActivation=0
    for n in wordmap:
        n.activation=0
        n.caluForm.clear()
        for nunion in n.behindNode:
            nunion["isPass"]=False
        for nunion in n.frontNode:
            nunion["isPass"]=False
        for pair in n.synonymNode:
            pair["isPass"]=False