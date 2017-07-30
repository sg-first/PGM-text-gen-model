import node
import wordmapOp

#句级摘要对句子进行，得到的是所有摘要词组成的摘要块。其中，摘要块元素为parentNode，负责激发它的子节点。当一个摘要块中的元素全部施行激发后，产生的就是
#被摘要的句子。由于摘要块代表的是句子，所以摘要块之间存在接边。摘要块的集合即为network，通过用户指定激发数个摘要块（或自定义摘要块激发），network自动
#产生一个摘要块序列，序列中每个摘要块的每个元素向下激发，产生实际的句子，连接起来即为篇章

class parentNode:
    char = "" # 标记的摘要词
    sonNode= [] #[{node,activation}]，子节点

    def addsonNode(self,wnode,activation):
        self.sonNode.append({"node":wnode,"activation":activation}) #训练前的激活值先置1吧

    def activeSon(self):
        for son in self.sonNode:
            wordmapOp.nodeConduct(son["node"],son["activation"])

    def __init__(self,char):
        self.char=char

def charFindNode(list,char):
    return node.charFindNode(list,char)

# allpnode为所有parentNode的集合，这样做的目的是使得所有同样标记的pnode共用一个sonNode（即不重复）
def findornew(allpnode,char):
    nw1 = charFindNode(allpnode, char)
    if nw1 is None:
        nw1 = parentNode(char)
        allpnode.append(nw1)
    return nw1

# 注意，pnBlock的集合，即network可完全通过allpnode中的元素自定义而不用经由训练文本自动生成
class pnBlock:
    sen = None  # 标记的所描述的那个原始句子
    block = None #[parentNode]
    behindNode = []  # [{pnBlock,P,isPass}]，后向接边
    frontNode = []  # 前向接边
    firstp = 0 #该摘要块在段落中出现在首的次数
    activation = 0

    def dirChangeNode(self,sen,apnBlock,delta,nodelist):
        # 首先通过sen从已有的接边里找，找到就直接改P
        for nunion in nodelist:
            if nunion["node"].sen == sen:
                nunion["P"] += delta
                return nunion
        # 找不到直接添加apnBlcok
        newelm={"pnBlock":apnBlock,"P":delta,"isPass":False}
        nodelist.append(newelm)
        return newelm

    def dirChangeBehindNode(self, sen, apnBlock, delta):
        self.dirChangeNode(sen,apnBlock,delta,self.behindNode)

    def dirChangeFrontNode(self,sen,apnBlock,delta):
        self.dirChangeNode(sen,apnBlock,delta,self.frontNode)

    def changeNode(self, apnblock, delta, nodelist):  # Private
        # 训练集中所有句子都视为不同，所以在接边创建阶段没有相同的接边可供合并
        newelm={"pnBlock":apnblock,"P":delta,"isPass":False}
        nodelist.append(newelm)
        return newelm

    def changeBehindNode(self,apnblock,delta):
        self.changeNode(apnblock,delta,self.behindNode)

    def changeFrontNode(self,apnblock,delta):
        self.changeNode(apnblock,delta,self.frontNode)

    def activeBlock(self,wordmap):
        for pnode in self.block:
            pnode.activeSon()
        senpair = wordmapOp.getsenpair(wordmap)
        wordmapOp.clearActivation(wordmap)
        return wordmapOp.getmaxsen(senpair)

    def __init__(self,block,sen):
        self.block=block
        self.sen=sen