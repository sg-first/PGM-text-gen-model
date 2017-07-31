import parameter
import help
import pulp

constraints=[]
targetVariable=[]
weightIndex={} # 映射原文件名到目标变量
slackVariable=[]

def selectTarget(wordmap,relSen): #传导后进行此步骤。pulic
    for wn in wordmap:
        if wn.activation>parameter.minactive and not help.isExist(relSen,wn.char):
            constraints.append(wn.caluForm+'<='+str(parameter.minactive))
            continue
        if wn.activation<parameter.minactive and help.isExist(relSen,wn.char):
            constraints.append(wn.caluForm+'>='+str(parameter.minactive))
            continue

def creatModel():
    return pulp.LpProblem(sense=pulp.LpMinimize)

def addVar(name):
    var=pulp.LpVariable(name,lowBound=0)
    weightIndex[name]=var
    targetVariable.append(var)
    return 'targetVariable['+str(len(targetVariable)-1)+']'

def genTargetFunction(model,num): #松弛变量序号从0到num，该函数必须在proceCondition之前调用
    tf=''
    for i in range(num+1):
        name='slackVariable['+str(i)+']'
        slackVariable.append(pulp.LpVariable(name,lowBound=0))
        tf+=name
        if not i==num:
            tf+='+'
    tf='model+='+tf
    exec(tf)

def proceCondition(condition,model,num): #condition为文本形式
    allvar = condition.split('+')
    allvar = help.repeatSplitStr(allvar, '*')
    allvar = help.repeatSplitStr(allvar, '>=')
    allvar = help.repeatSplitStr(allvar, '<=')
    for i in range(len(allvar)):
        if i != len(allvar) - 1 and not allvar[i].isdigit():
            newname=addVar(allvar[i]) #定义约束条件中的目标变量
            condition=condition.replace(allvar[i],newname) #给约束条件中的变量进行换名

    slackVal='slackVariable['+str(num)+']' #加入扩大可行域的松弛变量
    if condition.find('>')==-1: #左侧目标变量系数都为正，右侧松弛变量大减小加
        condition = 'model+=' + condition + '-' + slackVal
    else:
        condition = 'model+=' + condition + '+' + slackVal

    exec(condition) #加入该约束条件

def train(): #pulic
    model=creatModel()
    genTargetFunction(model,len(constraints)-1) #有多少个约束条件有多少个松弛变量
    for i in range(len(constraints)):
        proceCondition(constraints[i],model,i)
    model.solve()

def updateWeights(allpnode):
    for i in weightIndex.keys():
        update=i+'='+str(weightIndex[i].varValue)
        exec(update)
    #自动清理
    constraints.clear()
    targetVariable.clear()
    weightIndex.clear()
    slackVariable.clear()