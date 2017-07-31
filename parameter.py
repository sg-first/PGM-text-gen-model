activeThreshold=5  # 词节点的可激活阈值
minactive=30  # 备选词最低激活值
minp=-33.0482  # 备选句子最低生成概率（log2(0.4^25)）
minstop=0.2  # 舍弃停用词的概率

simThreshold=0.85 # 句子被视为相似的阈值 fix:还没设置
activeThresholdB=5  # 块节点的可激活阈值
minactiveB=30  # 备选块最低激活值
minpB=-33.0482  # 备选块序列最低生成概率
radomWeight=False #wordmap未训练权值是否随机