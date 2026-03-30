# 如何使用已有的知识库 Car_Seat

## ✅ 已完成配置

工作流已配置为自动引用你的知识库 **Car_Seat**！

---

## 🔍 验证知识库是否正常工作

### 步骤1：检查知识库是否有内容

```bash
# 搜索知识库 Car_Seat
coze-coding-ai knowledge search \
  --query "汽车座椅" \
  --top-k 5
```

**预期输出：**
```
Found X results:
[Score: 0.xx] 汽车座椅相关知识内容...
```

**如果返回 0 条结果：**
- 知识库可能为空，需要先添加知识
- 或知识库名称不正确

---

### 步骤2：运行工作流测试

```bash
# 运行工作流
python src/main.py -m flow

# 查看输出中的 knowledge_count
# 如果 > 0，说明知识库引用成功
```

---

## 📚 如何添加知识到 Car_Seat

### 方式一：使用CLI命令

```bash
# 导入文本知识（注意：参数是 --dataset，不是 --table-name）
coze-coding-ai knowledge add \
  --dataset "Car_Seat" \
  --content "汽车座椅智能化趋势：AI自适应调节、健康监测、场景联动、个性化定制"

# 或使用简写
coze-coding-ai knowledge add \
  -d "Car_Seat" \
  -c "汽车座椅智能化趋势：AI自适应调节、健康监测、场景联动、个性化定制"

# 导入URL知识
coze-coding-ai knowledge add \
  --dataset "Car_Seat" \
  --url "https://example.com/seat-innovation-report"

# 批量导入
coze-coding-ai knowledge add \
  --dataset "Car_Seat" \
  --content "$(cat your_knowledge.txt)"
```

### 方式二：使用Python代码

```python
from coze_coding_dev_sdk import KnowledgeClient, KnowledgeDocument, DataSourceType

client = KnowledgeClient()

# 添加知识（注意：参数是 table_name，不是 dataset）
docs = [
    KnowledgeDocument(
        source=DataSourceType.TEXT,
        raw_data="""
        汽车座椅行业知识：
        1. 智能座椅核心功能：AI自适应调节、健康监测、场景联动
        2. 新材料应用：镁合金骨架、ACF仿生吸能材料、生物基面料
        3. 市场趋势：2026年智能座椅渗透率将达35%
        """
    )
]

response = client.add_documents(
    documents=docs,
    table_name="Car_Seat"  # Python SDK 使用 table_name
)

print(f"✅ 已添加 {len(response.doc_ids)} 条知识到 Car_Seat")
```

---

## 🎯 推荐添加的知识类型

### 1. 行业知识

```
- 汽车座椅行业年度报告
- 智能座舱发展趋势
- 新能源车座椅创新案例
```

### 2. 技术知识

```
- AI技术应用场景
- 新材料技术规格
- 座椅设计标准
```

### 3. 用户研究

```
- 用户需求调研报告
- 用户体验案例分析
- 市场反馈数据
```

### 4. 竞品分析

```
- 竞品座椅功能对比
- 创新案例研究
- 专利技术分析
```

### 5. 项目经验

```
- 成功案例分析
- 失败教训总结
- 优化建议记录
```

---

## ⚙️ 高级配置

### 调整检索参数

编辑 `src/graphs/nodes/knowledge_search_node.py`：

```python
response = client.search(
    query=query,
    table_names=["Car_Seat"],
    top_k=15,        # 增加检索条数（默认10）
    min_score=0.6    # 提高相似度要求（默认0.5）
)
```

**参数说明：**
- `top_k`: 检索返回的知识条数
- `min_score`: 相似度阈值（0.0-1.0），越高越严格

### 检索多个知识库

```python
response = client.search(
    query=query,
    table_names=["Car_Seat", "其他知识库名"],  # 可以指定多个
    top_k=10
)
```

---

## 📊 验证效果

### 运行测试

```bash
# 1. 添加测试知识
coze-coding-ai knowledge add \
  --table-name Car_Seat \
  --content "测试知识：AI自适应座椅可根据用户体型自动调整支撑"

# 2. 运行工作流
python src/main.py -m flow

# 3. 查看输出
# 应该看到：
# ✅ 从知识库 'Car_Seat' 检索到 X 条相关知识
# knowledge_count: X
```

---

## 🔍 故障排查

### 问题1：knowledge_count 为 0

**可能原因：**
1. 知识库为空
2. 检索关键词不匹配
3. 相似度阈值过高

**解决方案：**
```bash
# 1. 检查知识库内容
coze-coding-ai knowledge search --query "汽车座椅"

# 2. 降低相似度阈值（编辑代码）
min_score=0.3  # 从0.5降到0.3

# 3. 添加更多相关知识
coze-coding-ai knowledge add --table-name Car_Seat --content "..."
```

### 问题2：知识库不存在

**错误信息：** `Table Car_Seat not found`

**解决方案：**
```bash
# 自动创建知识库（添加时会自动创建）
coze-coding-ai knowledge add \
  --dataset "Car_Seat" \
  --content "第一条知识"
```

### 问题3：检索不到相关知识

**原因：** 关键词不匹配

**解决方案：**
```python
# 修改查询关键词（在代码中）
query = "汽车座椅 " + " ".join(search_keywords[:5])  # 增加关键词
```

---

## 🎯 最佳实践

### 1. 知识库内容建议

```
✅ 好的知识：
- 结构清晰、内容完整
- 包含具体案例和数据
- 与座椅行业高度相关

❌ 不好的知识：
- 过于碎片化
- 缺乏上下文
- 与座椅无关
```

### 2. 定期维护

```bash
# 定期搜索验证知识库质量
coze-coding-ai knowledge search --query "AI座椅" --top-k 10

# 更新过时知识
# 删除错误知识
# 添加最新知识
```

### 3. 知识库分类

建议创建多个专题知识库：
- `Car_Seat_Tech` - 技术知识
- `Car_Seat_Market` - 市场知识
- `Car_Seat_User` - 用户研究

---

## 📈 效果展示

### 添加知识前

```
📊 本次共分析 20 条资讯，引用 0 条历史知识
```

### 添加知识后

```
📊 本次共分析 20 条资讯，引用 8 条历史知识

## 📊 行业动态概览
[结合网络资讯和历史知识的深度分析]
```

---

## ✅ 快速验证清单

- [ ] 知识库 Car_Seat 已创建
- [ ] 知识库中有内容（运行搜索命令验证）
- [ ] 工作流运行成功
- [ ] knowledge_count > 0
- [ ] 推送内容包含知识库引用

---

## 📞 需要帮助？

如果遇到问题，请：
1. 检查知识库是否有内容
2. 查看工作流运行日志
3. 调整检索参数
4. 添加更多高质量知识

---

**现在你的工作流已经配置为自动使用知识库 Car_Seat！** 🎉
