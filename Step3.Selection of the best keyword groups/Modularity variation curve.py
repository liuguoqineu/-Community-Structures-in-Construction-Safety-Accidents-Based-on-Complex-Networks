import matplotlib.pyplot as plt

# 读取数据
file_path = 'mokuaidu.txt'  # 替换为你的实际路径
modularity_list = []
community_count_list = []

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        if line.startswith("模块度"):
            modularity = float(line.split(":")[1].strip())
            modularity_list.append(modularity)
        elif line.startswith("社区数量"):
            community_count = int(line.split(":")[1].strip())
            community_count_list.append(community_count)

# x轴为关键字的序号
x = list(range(1, len(modularity_list) + 1))

# 创建图像
plt.figure(figsize=(12, 6))
plt.suptitle('关键字加入后社区结构变化趋势图', fontsize=16, fontweight='bold')

# Subplot 1: Modularity Variation
plt.subplot(1, 2, 1)
plt.plot(x, modularity_list, linestyle='-', color='blue', label='Modularity')
plt.xlabel('Keyword Index', fontsize=12)
plt.ylabel('Modularity', fontsize=12)
plt.title('Modularity Variation Curve', fontsize=14)
plt.grid(True)
plt.legend()

# Subplot 2: Community Count Variation
plt.subplot(1, 2, 2)
plt.plot(x, community_count_list, linestyle='--', color='green', label='Number of Communities')
plt.xlabel('Keyword Index', fontsize=12)
plt.ylabel('Number of Communities', fontsize=12)
plt.title('Community Count Variation Curve', fontsize=14)
plt.grid(True)
plt.legend()


plt.tight_layout(rect=[0, 0, 1, 0.95])  # 调整布局避免标题遮挡

# ✅ 一定要在 show() 之前保存！加 bbox_inches 保证标签不被裁剪
plt.savefig('community_modularity_trends.png', dpi=300, bbox_inches='tight')

plt.show()

