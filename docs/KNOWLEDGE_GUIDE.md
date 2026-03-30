# 知识库集成使用指南

## ✅ 功能已集成

工作流已成功集成 **Coze 长期记忆库（知识库）** 功能！

---

## 🎯 工作流程

```
搜索节点 → 知识库检索节点 → 分析节点 → 飞书推送节点
    ↓            ↓               ↓
  网络资讯    历史知识      结合两者分析
    └────────────┴───────────────┘
              ↓
          综合报告
```

---

## 📚 如何使用知识库

### 1. 添加知识到知识库

#### 方式一：使用CLI命令（推荐）

```bash
# 导入文本知识
coze-coding-ai knowledge add \
  --dataset coze_doc_knowledge \
  --content "汽车座椅智能化发展的五大趋势：1. AI自适应调节 2. 健康监测 3. 场景化设计 4. 轻量化材料 5. 环保材料应用"

# 导入URL知识
coze-coding-ai knowledge add \
  --dataset coze_doc_knowledge \
  --url "https://example.com/seat-innovation-trend"

# 批量导入文档
coze-coding-ai knowledge add \
  --dataset coze_doc_knowledge \
  --content "$(cat knowledge_base.txt)"
```

#### 方式二：使用Python代码

```python
from coze_coding_dev_sdk import KnowledgeClient, KnowledgeDocument, DataSourceType

client = KnowledgeClient()

# 添加文本知识
docs = [
    KnowledgeDocument(
        source=DataSourceType.TEXT,
        raw_data="汽车座椅行业知识：智能座椅已成为新能源汽车的核心竞争力..."
    )
]

response = client.add_documents(
    documents=docs,
    table_name="coze_doc_knowledge"
)

print(f"已添加 {len(response.doc_ids)} 条知识")
```

---

### 2. 知识库检索配置

当前工作流会自动：
- 从网络搜索结果中提取关键词
- 从知识库检索相关历史知识（最多10条）
- 相似度阈值：0.5（可调整）

**修改检索参数：**

编辑 `src/graphs/nodes/knowledge_search_node.py`:

```python
response = client.search(
    query=query,
    top_k=10,        # 检索条数
    min_score=0.5    # 相似度阈值（0.0-1.0）
)
```

---

### 3. 查看知识库内容

```bash
# 搜索知识库
coze-coding-ai knowledge search \
  --query "汽车座椅 AI技术" \
  --top-k 5
```

---

## 💡 推荐添加的知识类型

### 1. 行业趋势报告
```
汽车座椅行业年度报告
智能座舱发展趋势
新能源车座椅创新案例
```

### 2. 技术知识库
```
AI技术应用场景
新材料技术规格
座椅设计标准
```

### 3. 用户研究
```
用户需求调研报告
用户体验案例分析
市场反馈数据
```

### 4. 竞品分析
```
竞品座椅功能对比
创新案例研究
专利技术分析
```

### 5. 历史项目经验
```
成功案例分析
失败教训总结
优化建议记录
```

---

## 🔄 知识库的作用

### 分析报告会更全面

**仅网络资讯：**
- 只能看到最新的行业动态
- 缺乏历史背景和经验参考

**网络资讯 + 知识库：**
- ✅ 最新行业动态
- ✅ 历史趋势对比
- ✅ 经验教训参考
- ✅ 深度分析能力

---

## 📊 效果示例

### 推送内容展示

```
🚗 汽车座椅产品规划日报 - 2026年03月30日

📊 本次共分析 20 条资讯，引用 5 条历史知识

## 📊 行业动态概览
[结合网络资讯和历史知识的综合分析]

## 📈 核心趋势洞察
[对比历史趋势的深度洞察]

## 💡 创新方向建议
[基于历史经验的可落地建议]

## 🔍 重点关注
[基于长期积累的重点识别]

## 📚 参考资料
[资讯来源 + 知识库引用]
```

---

## 🚀 快速开始

### 1. 初始化知识库

```bash
# 创建知识库文件
cat > knowledge_init.txt << EOF
汽车座椅行业知识：

1. 智能座椅核心功能：
   - AI自适应调节：根据体型和坐姿自动调整支撑
   - 健康监测：心率、呼吸、疲劳度监测
   - 场景联动：与座舱系统协同工作
   - 个性化定制：记忆用户偏好设置

2. 新材料应用：
   - 轻量化：镁合金、碳纤维骨架
   - 环保材料：生物基材料、再生材料
   - 舒适材料：ACF仿生吸能材料、相变材料

3. 行业趋势：
   - 2026年智能座椅渗透率将达35%
   - 新能源车型座椅单价较燃油车高35%
   - 环保材料应用比例2025年将达25%
EOF

# 导入知识库
coze-coding-ai knowledge add \
  --dataset coze_doc_knowledge \
  --content "$(cat knowledge_init.txt)"
```

### 2. 运行工作流

```bash
# 启动工作流服务
python src/main.py -m http -p 5000 &

# 启动定时服务
bash start_scheduler.sh
```

### 3. 查看效果

检查推送内容中是否包含知识库引用：
```
📊 本次共分析 20 条资讯，引用 X 条历史知识
```

---

## ⚙️ 高级配置

### 自定义检索策略

编辑 `src/graphs/nodes/knowledge_search_node.py`:

```python
# 从网络搜索结果中提取更多关键词
search_keywords = []
for result in state.search_results[:10]:  # 扩展到前10条
    title = result.get("title", "")
    snippet = result.get("snippet", "")
    if title:
        search_keywords.append(title)

# 调整检索参数
response = client.search(
    query=query,
    top_k=15,        # 增加检索条数
    min_score=0.6    # 提高相似度要求
)
```

### 分数据集检索

```python
# 可以指定特定数据集
response = client.search(
    query=query,
    table_names=["seat_trends", "user_research"],  # 指定数据集
    top_k=10
)
```

---

## 📈 最佳实践

### 1. 定期更新知识库
- 每周添加最新的行业报告
- 记录重要的项目经验
- 更新竞品分析数据

### 2. 分类管理知识
- 行业趋势库
- 技术知识库
- 用户研究库
- 项目经验库

### 3. 验证知识质量
- 定期搜索验证
- 清理过时知识
- 更新错误信息

### 4. 持续优化检索
- 调整相似度阈值
- 优化关键词提取
- 监控检索效果

---

## ❓ 常见问题

### Q1: 知识库检索返回0条怎么办？

**原因：** 知识库为空或相似度不够

**解决：**
1. 添加相关知识到知识库
2. 降低 `min_score` 阈值（默认0.5）
3. 优化检索关键词

### Q2: 如何查看知识库是否被使用？

**检查方式：**
查看推送内容中的 `knowledge_count` 数量

### Q3: 知识库会影响推送速度吗？

**影响：**
- 知识库检索耗时约 1-3秒
- 总体影响很小，可接受

### Q4: 如何删除错误的知识？

```bash
# 目前需要通过管理界面删除
# 或联系管理员清理数据集
```

---

## ✅ 功能验证

运行测试确认知识库集成成功：

```bash
# 运行工作流
python src/main.py -m flow

# 查看输出
# 应包含：knowledge_count: X
```

---

**现在你的工作流已经具备知识库能力，可以积累和利用长期记忆了！** 🎉
