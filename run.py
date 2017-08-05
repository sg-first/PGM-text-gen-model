import wordmapOp
import networkOp
import help
import lang
import training

lang.init("D:/NLP/paper1/stopWordList(gen).txt","D:/NLP/paper1/synonymsList(gen).txt")
txt=help.readTXT("D:/NLP/paper1/123.txt")
tsenllist=txt.split("\n")
print("载入词典与读取训练文本完成！")

# 训练部分：
# sen是句子，senlist是篇章，senllist是所有训练篇章。一开始有文本形式的数组tsenllist，元素为文本形式的tsenlist
senllist=[]
for tsenlist in tsenllist:
    senlistsou = lang.segWord(tsenlist)
    senlist = help.splitList(senlistsou,"。")
    del senlist[len(senlist) - 1] #去除尾部空列
    senllist.append(senlist)
print("切割训练文本完成！")

wordmap=[]
for senlist in senllist:
    for sen in senlist:
        wordmapOp.genWordMap(wordmap,sen)
print("wordmap生成完成！")
wordmapOp.normalizedWeight(wordmap,senllist)
print("wordmap归一化完成！")

allpnode=[]
network=[]
for senlist in senllist:
    networkOp.genNetwork(network,wordmap,allpnode,senlist)
print("network生成完成！")
networkOp.normalizedWeight(network,senllist)
print("network归一化完成！")

# 训练
for b in network:
    training.relTrain(b,wordmap,allpnode)
print("allpnode向下激活权值训练完成！")

def findNode(word):
    for i in wordmap:
        if i.word==word:
            return i

def findpNode(word):
    for i in allpnode:
        if i.word==word:
            return i

def printAllpNode():
    for i in allpnode:
        print(i.word)

def findBlock(sen):
    for i in network:
        if i.sen==sen:
            return i

def clear():
    wordmapOp.clearActivation(wordmap)
    networkOp.clearActivation(network)

def blistGen(blist): # 直接按顺序生成块序列，不传导
    return networkOp.genChapter(blist,wordmap)

def blockConductGen(blist,activationList): # 传导后生成块序列
    for i in range(len(blist)):
        networkOp.blockConduct(blist[i],activationList[i])
    blpair=networkOp.getblpair(network)
    blist=networkOp.getmaxblist(blpair)
    result=networkOp.genChapter(blist,wordmap)
    networkOp.clearActivation(network)
    return result

def nodeConductGen(nlist,activationList):
    tool=[{'coefficient':1,'variable':'a'}]
    for i in range(len(nlist)):
        wordmapOp.nodeConduct(nlist[i],activationList[i],tool)
    senpair=wordmapOp.getsenpair(wordmap)
    print(help.tojson(senpair))
    wordmapOp.clearActivation(wordmap)
    sen=wordmapOp.getmaxsen(senpair)
    return help.listToStr(sen)

# 另外还有常用操作，如实例化pnBlock，改变firstp，添加接边。均可以在import parentNode后手动进行，这里不再提供应用级接口