import networkx as nx
import community.community_louvain as community_louvain
import pandas as pd
import os
import gc
from collections import Counter

# **定义文件**
quguanjianci_file = 'quguanjianci.txt'
shanchu_file = 'shanchu.txt'
shiyong_file = 'shiyong.txt'
mokuaidu_file = 'mokuaidu.txt'
tu_file = 'tu.xlsx'  # 存储网络结构的 Excel 文件
batch_size = 100  # 每 100 条边写入一次 Excel

# **清空或创建文件**
for filename in [quguanjianci_file, shanchu_file, shiyong_file, mokuaidu_file]:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("")

# **初始化变量**
matched_keywords = set()
used_keywords = set()  # 记录已提取的关键词，防止重复处理
edge_count = 0
max_edges = 20000
keyword_edge_count = {}
deleted_keywords = set()
tu_data = []  # 存储网络结构数据

# **读取 Excel 文件**
guanjianci_df = pd.read_excel('Edge formation results from expert evaluation.xlsx', dtype=str)
zhuanjiadafen_df = pd.read_excel('Expert-scored keywords.xlsx', dtype=str)

# **初始化网络**
G = nx.Graph()

# **定义写入 Excel 的函数**
def save_to_excel():
    global tu_data
    if tu_data:
        df = pd.DataFrame(tu_data, columns=['source', 'target', 'keyword'])
        if not os.path.exists(tu_file):
            df.to_excel(tu_file, index=False)  # 第一次写入新文件
        else:
            with pd.ExcelWriter(tu_file, mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
        tu_data = []  # 清空数据列表
        print(f"已保存 {len(df)} 条边到 {tu_file}")

# **处理关键词**
def process_keywords():
    global edge_count, tu_data

    for index, row in zhuanjiadafen_df.iterrows():
        if edge_count >= max_edges:
            print(f"全局边数达到最大限制 {max_edges}，停止处理。")
            break  # 停止处理

        keyword = str(row['严重事故']).strip()

        # **记录取出的关键词**
        with open(quguanjianci_file, 'a', encoding='utf-8') as f:
            f.write(keyword + '\n')

        # **跳过已处理的关键词**
        if keyword in used_keywords:
            print(f"关键词 '{keyword}' 已处理过，跳过。")
            continue
        used_keywords.add(keyword)

        print(f"处理关键词: {keyword} (索引: {index})")

        # **匹配 guanjianci.xlsx**
        matched = False  # 标记该关键词是否有效
        temp_edges = []  # 存储本关键词的边

        for _, guanjianci_row in guanjianci_df.iterrows():
            if edge_count >= max_edges:
                print(f"全局边数达到最大限制 {max_edges}，停止处理。")
                break  # 停止匹配

            if keyword in guanjianci_row['通报']:
                # **统计关键词的边数**
                if keyword not in keyword_edge_count:
                    keyword_edge_count[keyword] = 0
                keyword_edge_count[keyword] += 1

                print(f"  找到匹配的关键词 '{keyword}'，边数计数: {keyword_edge_count[keyword]}")

                # **如果关键词的边数超过 100，立即存入 shanchu.txt，并跳过处理**
                if keyword_edge_count[keyword] > 100:
                    if keyword not in deleted_keywords:
                        deleted_keywords.add(keyword)
                        print(f"  关键词 '{keyword}' 超过 100 次，跳过该关键词。")

                        # **即时写入 shanchu.txt**
                        with open(shanchu_file, 'a', encoding='utf-8') as f:
                            f.write(keyword + '\n')

                    # **关键改动：一旦超过 100 次，不写入 tu.xlsx**
                    break  # 直接退出当前关键词的匹配循环

                matched = True  # 该关键词至少匹配了一条边，且未被抛弃
                matched_keywords.add(keyword)
                edge = (guanjianci_row[1], guanjianci_row[2])  # 构造边
                temp_edges.append(edge)  # 临时存储
                tu_data.append([guanjianci_row[1], guanjianci_row[2], keyword])

                edge_count += 1
                print(f"  添加边: {guanjianci_row[1]} -> {guanjianci_row[2]} (关键词: {keyword})")

                if edge_count >= max_edges:
                    print(f"  达到最大边数限制 {max_edges}，停止处理。")
                    break  # 停止匹配

        # **如果关键词有效且未超 100 次，则加入网络并计算社区指标**
        if matched and keyword not in deleted_keywords:
            G.add_edges_from(temp_edges)  # 添加边到图

            # **计算 Louvain 社区**
            partition = community_louvain.best_partition(G)
            modularity = community_louvain.modularity(partition, G)

            # **修正计算社区大小**
            community_counts = Counter(partition.values())  # 统计每个社区的大小
            community_sizes = list(community_counts.values())  # 转换为列表
            num_communities = len(community_counts)  # 社区的总数量

            # **写入 mokuaidu.txt**
            with open(mokuaidu_file, 'a', encoding='utf-8') as f:
                f.write(f"加入的关键字：{keyword}\n")
                f.write(f"模块度: {modularity}\n")
                f.write(f"社区数量: {num_communities}\n")
                f.write(f"社区大小的分布: {community_sizes}\n\n")

            with open(shiyong_file, 'a', encoding='utf-8') as f:
                f.write(keyword + '\n')

        # **定期写入 Excel 以减少内存占用**
        if len(tu_data) >= batch_size:
            save_to_excel()

        # **定期释放内存**
        if index % 10 == 0:
            gc.collect()

# **执行处理**
# **执行处理**
process_keywords()

# **最终写入 Excel**
save_to_excel()

# **打印图的基本信息**
print(f"最终创建的图中共有 {G.number_of_nodes()} 个节点，{G.number_of_edges()} 条边。")

print(f"处理完成，共找到 {edge_count} 条边。")
print(f"网络结构已保存至 {tu_file}")

