import json
import help

def init(path):
    jsoncode=help.readTXT(path)
    global synlist
    synlist=json.loads(jsoncode)

def getid(word):
    now1=help.gethead(word)
    now2=help.gethead2(word)
    if now1 in synlist.keys():
        if now2 in synlist[now1].keys():
            for i in synlist[now1][now2]:
                if i[0]==word:
                    return i[1]
    return -1

def getDistance(word1,word2):
    id1=getid(word1)
    id2=getid(word2)
    if id1==-1 or id2==-1:
        return -1
    else:
        return abs(id1-id2)

def isSynonyms(word1,word2,threshold=0):
    distance=getDistance(word1,word2)
    if distance==-1:
        return False
    else:
        return distance<=threshold