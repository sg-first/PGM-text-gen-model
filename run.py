import wordmapOp
import help
import lang

lang.init("D:/TCproject/NLP/paper1/stopWordList(gen).txt","D:/TCproject/NLP/paper1/synonymsList(gen).txt")
#sen是句子，senlist是篇章，senllist是所有训练篇章。一开始有文本形式的数组tsenllist，元素为文本形式的tsenlist
senllist=[]
for tsenlist in tsenllist:
    senlistsou=lang.segWord(tsenlist)
    senlist=help.splitList(senlistsou,"。")
    senllist.append(senlist)

wordmap=[]
for senlist in senllist:
    for sen in senlist:
        wordmap=wordmapOp.genWordMap(wordmap,sen)
wordmapOp.normalizedWeight(wordmap,wllist)
#fix:两层摘要边创建后，从句摘要边向上，逐层训练权值
#生成部分：先选定高层摘要边，向下产生句摘要边
for w in qwlist: #qwlist为句摘要边的特征词列表，[char,activateSignal]
    wordmapOp.wordconduct(wordmap,w[0],w[1])
senpair=wordmapOp.getsenpair(wordmap)
sen=help.getmax(senpair)
wordmapOp.clearactivation(wordmap)