import pandas as pd
from itertools import combinations

# 读取连边关键词
with open('Cumulative keyword results.txt', 'r', encoding='utf-8') as f:
    edge_keywords = set(f.read().strip().split())  # 按空格分词


# 读取安全事故新闻报道表格
file_path = 'Safety accident news reports.xlsx'
df = pd.read_excel(file_path)

# 确保关键列存在
required_columns = ['序号', '关键词']
if not all(col in df.columns for col in required_columns):
    raise ValueError("表格缺少必要的列: '序号' 或 '关键词'")

# 构建 {序号: 关键词集合} 结构
doc_keywords = {
    row['序号']: set(str(row['关键词']).split( )) & edge_keywords  # 取交集
    for _, row in df.iterrows()
}

# 生成连边数据
data = []
for (id1, keywords1), (id2, keywords2) in combinations(doc_keywords.items(), 2):
    common_keywords = keywords1 & keywords2  # 取交集
    if common_keywords:
        data.append([id1, id2, ', '.join(common_keywords)])

# 保存到Excel
df_edges = pd.DataFrame(data, columns=['源节点', '目标节点', '共同关键词'])
df_edges.to_excel('Optimized edge relationships.xlsx', index=False)

print("连边数据已生成，保存在 'Optimized edge relationships.xlsx' 文件中。")