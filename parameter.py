activeThreshold=2  # 词节点的可激活阈值
minactive=3  # 备选词最低激活值
LPminactive=20 # 在规划求解中使用的带余地的激活阈值
minp=10000  # 备选句子最低生成概率
minstop=0.2  # 舍弃停用词的概率
stackWeights=0.9 # 叠加接边衰减
repeatLimit=1 # 生成实词的重复次数限制
maxLength=40 # 生成的句子的最大长度
topicTolerance=5 # 允许概率低于最低生成概率的最大句子长度
initActivation=6 #初激活值

simThreshold=0.85 # 句子被视为相似的阈值
activeThresholdB=2  # 块节点的可激活阈值
minactiveB=3  # 备选块最低激活值
minpB=0.9  # 备选块序列最低生成概率
stackWeightsB=0.9 # 叠加接边衰减
radomWeight = False # wordmap未训练权值是否随机
simMergers = False # 对相似句子计数并自动合并相似句子的接边。训练集量小时无效。关闭视所有句子都不相似，pnBlock接边仅按训练集序