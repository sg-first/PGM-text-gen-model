import json

def caluCount(list,elm):
    count=0
    for i in list:
        if i==elm:
            count+=1
    return count

def listToStr(list,sep=''):
    if list is None:
        return ""
    return sep.join(list)

def readTXT(path):
    return open(path,'r').read()

def getByIndex(list,sub):
    if sub<0 or sub>=len(list):
        return None
    else:
        return list[sub]

def gethead(str):
    return str[0:1]

def gethead2(str):
    return str[1:2]

def splitList(list,sep,result=None):
    if result is None:
        result=[]
    try:
        i=list.index(sep)
    except: # 不可再分
        result.append(list)
        return result
    else:
        result.append(list[:i])
        return splitList(list[i+1:],sep,result)

def tojson(list):
    return json.dumps(list,ensure_ascii=False)

def getmax(senpair,key):
    maxelm={key:None,"P":0}
    for i in senpair:
        if i["P"]>maxelm["P"]:
            maxelm=i
    return maxelm[key]

def repeatSplit(list,seq):
    listB=[]
    for i in list:
        listB+=splitList(i,seq)
    return listB

def repeatSplitStr(list,seq):
    listB=[]
    for i in list:
        listB+=i.split(seq)
    return listB

def isExist(list,elm):
    for i in list:
        if i==elm:
            return True
    return False

def limitDigits(num):
    return float(("%.2f" % num))

def isNum(num):
    try:
        float(num)
        return True
    except ValueError:
        return False