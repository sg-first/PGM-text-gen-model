import lang
import parameter
import help

class node:
    char = ""
    behindStop=[]  # [stopWord],句尾停用词
    frontStop=[]  # 句首停用词
    behindNode = []  # [{node,P,isPass,[stopWord]}]，后向接边
    frontNode = []  # 前向接边
    synonymNode = [] # [{node,isPass}]，同义边
    activation = 0
    firstp = 0  # 该词出现在句首的次数

    def changeNode(self, anode, delta, nodelist):  # Private
        for nunion in nodelist:
            if nunion["node"].char == anode.char:
                nunion["P"] += delta
                return nunion
        # 没有，添加
        newelm={"node":anode,"P":delta,"isPass":False,"stopList":[]}
        nodelist.append(newelm)
        return newelm

    def addStopWord(self,elmlist,word,delta):  # Private
        for i in elmlist:
            if i.char==word:
                i.p+=delta
                return
        # 没有，添加
        newStopWord=stopWord(word,delta)
        elmlist.append(newStopWord)

    def autoChangeBehindNode(self,node1,node2,word1,delta):
        if not lang.isStopWord(word1):
            self.changeNode(node1, delta, self.behindNode)
            return
        else:
            if node2 is None:  # 上层要至少保证word1不是None（不越界）
                self.addStopWord(self.behindStop, word1, delta)  # word1为尾词停止，调整behindStop
                return
            else:
                elm = self.changeNode(node2, delta, self.behindNode)
                self.addStopWord(elm["stopList"], word1, delta)
                return

    def autoChangeFrontNode(self,node1,node2,word1,delta):
        if not lang.isStopWord(word1):
            self.changeNode(node1, delta, self.frontNode)
            return
        else:
            if node2 is None:  # 上层要至少保证word1不是None
                self.addStopWord(self.frontStop, word1, delta)  # word1为尾词停止，调整frontStop
                return
            else:
                elm = self.changeNode(node2,delta,self.frontNode)
                self.addStopWord(elm["stopList"], word1, delta)
                return

    def addSynonyms(self,n):
        for spair in self.synonymNode:
            if spair["node"].char==self.char: #正面有，反面就有，反之亦然
                return
        self.synonymNode.append({"node": n, "isPass": False})
        n.synonymNode.append({"node": self, "isPass": False})

    def __init__(self, char):
        self.char = char

class stopWord:
    char = ""
    p = 0

    def __init__(self,char,delta):
        self.char=char
        self.p=delta

def genStopWord(elmlist):
    maxp=parameter.minstop
    maxstop=None
    for i in elmlist:
        if i.p>maxp:
            maxp=i.p
            maxstop=i.char
    return maxstop

def charFindNode(wordmap,char):
    for n in wordmap:
        if n.char==char:
            return n
    return None

def findornew(wordmap,char):
    nw1 = charFindNode(wordmap, char)
    if nw1 is None:
        nw1 = node(char)
        wordmap.append(nw1)
    return nw1

def charFindNodeList(wordmap,charList):
    result=[]
    for n in wordmap:
        for c in range(charList):
            if n.char==charList[c]:
                result.append(n)
                charList=help.listDel(charList,c)
                break
    return result