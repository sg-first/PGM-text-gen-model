import node
import wordmapOp
import help

#句级摘要对句子进行，得到的是所有摘要词组成的摘要块。其中，摘要块的元素为parentNode，负责激发它的子节点。当一个摘要块中的元素全部施行激发后，产生的就是
#被摘要的句子。由于摘要块代表的是句子，所以摘要块之间存在接边。摘要块的集合即为network，通过用户指定激发数个摘要块（或自定义摘要块激发），network自动
#产生一个摘要块序列，序列中每个摘要块的每个元素向下激发，产生实际的句子，连接起来即为篇章

class parentNode:
    word = "" # 标记的摘要词
    sonNode = None #[{node,activation}]，子节点
    sub = -1

    def addsonNode(self,wnode,activation):
        for sonpair in self.sonNode:
            if sonpair["node"].word == wnode.word:
                return
        self.sonNode.append({"node":wnode,"activation":activation}) #没有再添加

    def activeSon(self):
        for son in range(len(self.sonNode)):
            name='allpnode['+str(self.sub)+'].sonNode['+str(son)+'][\"activation\"]'
            formpair={'coefficient':1,'variable':name}
            wordmapOp.nodeConduct(self.sonNode[son]["node"],self.sonNode[son]["activation"],[formpair])

    def __init__(self,word):
        self.word=word
        self.sonNode = []

def wordFindNode(list,word):
    return node.wordFindNode(list,word)

# allpnode为所有parentNode的集合，这样做的目的是使得所有同样标记的pnode共用一个sonNode（即不重复）
def findornew(allpnode,word):
    nw1 = wordFindNode(allpnode, word)
    if nw1 is None:
        nw1 = parentNode(word)
        allpnode.append(nw1)
        nw1.sub=len(allpnode)-1
    return nw1

# 注意，pnBlock的集合（即network）可完全通过allpnode中的元素自定义而不用经由训练文本自动生成
class pnBlock:
    sen = ""  # 标记的所描述的那个原始句子
    senList = None
    block = None # [parentNode]
    behindNode = None  # [{pnBlock,P,isPass}]，后向接边
    frontNode = None  # 前向接边
    behindNodeStr = None
    frontNoneStr = None
    firstp = 0 #该摘要块在段落中出现在首的次数
    activation = 0
    simCount = 1

    def unionToStr(self,union):  # Private
        return "{"+union["pnBlock"].sen+","+str(union["P"])+"}"

    def genNodeStr(self,list):  # Private
        nodestr=""
        for union in list:
            nodestr+=self.unionToStr(union)+","
        return nodestr

    def relgenNodeStr(self):
        self.behindNodeStr=self.genNodeStr(self.behindNode)
        self.frontNoneStr=self.genNodeStr(self.frontNode)

    def isStrNotNone(self):
        return (not self.behindNodeStr is None) and (not self.frontNoneStr is None)

    def dirChangeNode(self,sen,apnBlock,delta,nodelist): # Private
        # 首先通过sen从已有的接边里找，找到就直接改P
        for nunion in nodelist:
            if nunion["pnBlock"].sen == sen:
                nunion["P"] += delta
                return nunion
        # 找不到直接添加apnBlcok
        newelm={"pnBlock":apnBlock,"P":delta,"isPass":False}
        nodelist.append(newelm)
        return newelm

    def dirChangeBehindNode(self, sen, apnBlock, delta): # 用于后期
        self.dirChangeNode(sen,apnBlock,delta,self.behindNode)

    def dirChangeFrontNode(self,sen,apnBlock,delta): # 用于后期
        self.dirChangeNode(sen,apnBlock,delta,self.frontNode)

    def changeNode(self, apnblock, delta, nodelist): # Private
        # 训练集中所有句子都视为不同，所以在接边创建阶段没有相同的接边可供合并
        newelm={"pnBlock":apnblock,"P":delta,"isPass":False}
        nodelist.append(newelm)
        return newelm

    def changeBehindNode(self,apnblock,delta):
        self.changeNode(apnblock,delta,self.behindNode)

    def changeFrontNode(self,apnblock,delta):
        self.changeNode(apnblock,delta,self.frontNode)

    def activeBlock(self,wordmap,isClear=True):
        for pnode in self.block:
            pnode.activeSon()
        senpair = wordmapOp.getsenpair(wordmap) # 得到所有可能的句对
        print(help.tojson(senpair)) # fix:debug
        if isClear:
            wordmapOp.clearActivation(wordmap)
        return wordmapOp.getmaxsen(senpair)

    def __init__(self,block,sen,senList):
        self.senList=senList
        self.block=block
        self.sen=sen
        self.behindNode = []
        self.frontNode = []