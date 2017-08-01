import wordmapOp
import networkOp
import help
import lang
import training

lang.init("D:/TCproject/NLP/paper1/stopWordList(gen).txt","D:/TCproject/NLP/paper1/synonymsList(gen).txt")

# 训练部分：
# sen是句子，senlist是篇章，senllist是所有训练篇章。一开始有文本形式的数组tsenllist，元素为文本形式的tsenlist
senllist=[]
for tsenlist in tsenllist:
    senlistsou = lang.segWord(tsenlist)
    senlist = help.splitList(senlistsou,"。")
    senllist.append(senlist)

wordmap=[]
for senlist in senllist:
    for sen in senlist:
        wordmapOp.genWordMap(wordmap,sen)
wordmapOp.normalizedWeight(wordmap,senllist)

allpnode=[]
network=[]
for senlist in senllist:
    networkOp.genNetwork(network,wordmap,allpnode,senlist)
networkOp.normalizedWeight(network,senllist)

# 训练
for b in network:
    training.relTrain(b,wordmap,allpnode)

# 底层的生成部分测试：直接激活一些词生成句子，假设选择wnlist
for wn in wnlist:
    wordmapOp.nodeConduct(wn,50,'nothing') # 随便激活一个，先50
senpair=wordmapOp.getsenpair(wordmap)
sen=wordmapOp.getmaxsen(senpair)
print(help.listToStr(sen))
wordmapOp.clearActivation(wordmap)

# 生成部分：先选定摘要块，自动向下生成，假设选择blist
for b in blist:
    networkOp.blockConduct(b,50) # 随便激活一个，先50
blpair=networkOp.getblpair(network)
blist=networkOp.getmaxblist(blpair)
print(networkOp.genChapter(blist,wordmap))
networkOp.clearActivation(network)
