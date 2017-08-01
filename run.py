import wordmapOp
import networkOp
import help
import lang
import training

lang.init("D:/TCproject/NLP/paper1/stopWordList(gen).txt","D:/TCproject/NLP/paper1/synonymsList(gen).txt")
txt=help.readTXT("D:/123.txt")
tsenllist=txt.split("\n")
print("载入词典与读取训练文本完成！")

# 训练部分：
# sen是句子，senlist是篇章，senllist是所有训练篇章。一开始有文本形式的数组tsenllist，元素为文本形式的tsenlist
senllist=[]
for tsenlist in tsenllist:
    senlistsou = lang.segWord(tsenlist)
    senlist = help.splitList(senlistsou,"。")
    senlist = help.listDel(senlist, len(senlist) - 1) #去除尾部空列
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

print("底层生成开始！")
# 底层的生成部分测试：直接激活一些词生成句子，假设选择wnlist
for wn in wordmap[3]:
    wordmapOp.nodeConduct(wn,50,'nothing') # 随便激活一个，先50
senpair=wordmapOp.getsenpair(wordmap)
#sen=wordmapOp.getmaxsen(senpair)
#print(help.listToStr(sen))
#wordmapOp.clearActivation(wordmap)
print(help.tojson(senpair))

print("高层生成开始！")
# 生成部分：先选定摘要块，自动向下生成，假设选择network[3]
for b in network[3]:
    networkOp.blockConduct(b,50) # 随便激活一个，先50
blpair=networkOp.getblpair(network)
blist=networkOp.getmaxblist(blpair)
print(networkOp.genChapter(blist,wordmap))
networkOp.clearActivation(network)