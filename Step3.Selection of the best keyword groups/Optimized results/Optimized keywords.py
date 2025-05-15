import re

# ========== 设置参数 ==========
input_path = "mokuaidu.txt"
output_path = "Cumulative keyword results.txt"
终止关键词 = "缆绳"  # ✅ 你想要截止的那个关键字内容

# ========== 读取并解析 ==========
with open(input_path, "r", encoding="utf-8") as f:
    content = f.read()

groups = content.strip().split("\n\n")

# ========== 提取关键词 ==========
keywords_list = []
for group in groups:
    match = re.search(r"加入的关键字：(.+)", group)
    if match:
        keyword = match.group(1).strip()
        keywords_list.append(keyword)
        if keyword == 终止关键词:
            break

# ========== 写入结果 ==========
with open(output_path, "w", encoding="utf-8") as f:
    f.write(" ".join(keywords_list))

print(f"✅ 已成功提取从第1组到关键字“{终止关键词}”为止的关键词，已保存为 {output_path}")
