import parameter
import help
import pulp
import wordmapOp

constraints=[]
targetVariable=[]
weightIndex={} # 映射原文件名到目标变量
slackVariable=[]

def simplify(condition): # 防止规划过程中递归过深，化简约束条件
    if len(condition)!=1:
        condition = mergeCoefficient(condition)
    newCondition=''
    for m in range(len(condition)):
        newCondition+=str(condition[m]['coefficient'])+'*'+condition[m]['variable']
        if m!=len(condition)-1:
            newCondition+='+'
    return newCondition

def mergeCoefficient(monomialList2):
    monomialList=[]
    monomialList.append({'coefficient':0,'variable':monomialList2[0]['variable']})
    for m2 in monomialList2:
        isfound = False
        for m in monomialList:
            if m2['variable']==m['variable']:
                m['coefficient']+=m2['coefficient'] # 有一样的就合并系数
                isfound=True
                break
        if not isfound:
            monomialList.append(m2) # 没有一样的就添加新项
    return monomialList

def selectTarget(wordmap,relSen): #传导后进行此步骤。pulic
    for wn in wordmap:
        if wn.activation>parameter.minactive and not help.isExist(relSen,wn.word):
            condition=simplify(wn.caluForm)
            constraints.append(condition+'<='+str(parameter.minactive))
            continue
        if help.isExist(relSen,wn.word): #and wn.activation<parameter.minactive: #只要需要出现的都加入约束条件，防止权值过小
            condition = simplify(wn.caluForm)
            constraints.append(condition+'>='+str(parameter.LPminactive))
            continue

def creatModel():
    return pulp.LpProblem(sense=pulp.LpMinimize)

def addVar(name):
    varname='targetVariable['+str(len(targetVariable))+']'
    var=pulp.LpVariable(varname,lowBound=parameter.activeThreshold)
    weightIndex[name]=var
    targetVariable.append(var)
    return varname

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
        if i != len(allvar) - 1 and not help.isNum(allvar[i]):
            newname=addVar(allvar[i]) #定义约束条件中的目标变量
            condition=condition.replace(allvar[i],newname) #给约束条件中的变量进行换名

    slackVal='slackVariable['+str(num)+']' #加入扩大可行域的松弛变量
    if condition.find('>=')!=-1: #左侧目标变量系数都为正，右侧松弛变量大减小加
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

def relTrain(apbBlock,wordmap,allpnode):
    apbBlock.activeBlock(wordmap,False) #只激活，不用管生成的是什么，而且不能清记录，训练后手动重置
    selectTarget(wordmap,apbBlock.senList)
    train()
    wordmapOp.clearActivation(wordmap)
    updateWeights(allpnode)