activeThreshold=5  # 词节点的可激活阈值
minactive=30  # 备选词最低激活值
minp=5  # 备选句子最低生成概率 fix:需要通过测试求得
minstop=0.2  # 舍弃停用词的概率
stackWeights=0.9 # 叠加接边衰减

simThreshold=0.85 # 句子被视为相似的阈值 fix:还没设置
activeThresholdB=5  # 块节点的可激活阈值
minactiveB=30  # 备选块最低激活值
minpB=5  # 备选块序列最低生成概率
stackWeightsB=0.9 # 叠加接边衰减
radomWeight=True #wordmap未训练权值是否随机
simMergers=False #对相似句子计数并自动合并相似句子的接边。训练集量小时无效。关闭视所有句子都不相似，pnBlock接边仅按训练集序