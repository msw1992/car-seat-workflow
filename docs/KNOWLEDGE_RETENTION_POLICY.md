# 知识库保留策略设计

## 背景

随着工作流每日运行，知识库会持续积累内容。为避免知识过时、检索效率下降和存储成本增加，需要建立智能的保留策略。

## 保留原则

### 按知识类型分层保留

| 知识类型 | 保留期限 | 过期策略 | 理由 |
|---------|---------|---------|------|
| **行业趋势** | 180天 | 自动过期 | 市场数据、技术趋势时效性强 |
| **技术案例** | 365天 | 降权保留 | 技术方案有长期参考价值，但需标记时效 |
| **用户洞察** | 365天 | 降权保留 | 用户需求相对稳定 |
| **项目经验** | 永久 | 永久保留 | 成功/失败经验有长期借鉴价值 |
| **竞品分析** | 90天 | 自动过期 | 竞品动态时效性最强 |

### 去重与更新策略

1. **相似度检测**：保存前检测相似内容（阈值0.85）
2. **内容更新**：发现相似内容时，比较保存时间，保留较新的
3. **质量评分**：评估置信度<0.7的内容标记为低质量

## 实施方案

### 方案A：基于元数据的过期清理（推荐）

**前提：需要知识库支持删除API**

```python
# 伪代码示例
def cleanup_expired_knowledge():
    """定期清理过期知识"""
    # 1. 检索所有知识
    all_docs = knowledge_client.list_all(table_name="Car_Seat")
    
    # 2. 检查过期时间
    for doc in all_docs:
        metadata = parse_metadata(doc)
        save_date = metadata.get("save_date")
        knowledge_type = metadata.get("knowledge_type")
        
        # 3. 根据类型判断是否过期
        if is_expired(save_date, knowledge_type):
            knowledge_client.delete(doc_id=doc.id)
            log.info(f"已删除过期知识: {doc.id}")
```

### 方案B：多知识库轮换策略

**不依赖删除API的方案**

```
知识库命名：Car_Seat_YYYYMM

策略：
- 每月创建新知识库
- 保留最近3个月的知识库（活跃使用）
- 第4个月的知识库归档或删除
- 分析时同时检索多个知识库
```

优点：
- ✅ 不需要删除API
- ✅ 自然过期机制
- ✅ 数据隔离安全

缺点：
- ❌ 检索时需要跨多个知识库
- ❌ 管理复杂度增加

### 方案C：标记降权策略

**当前最可行的方案**

```python
# 保存知识时添加过期标记
knowledge_content = f"""【{value_type}】汽车座椅产品规划日报 - {current_date}

{raw_content}

---
知识类型: {value_type}
评估置信度: {confidence}
保存时间: {current_date}
过期时间: {calculate_expiry_date(value_type)}  # 根据类型计算
时效性标记: {calculate_timeliness(current_date, value_type)}  # 新鲜/正常/过时
"""

# 检索时过滤过时内容
search_response = knowledge_client.search(
    query=search_query,
    table_names=[knowledge_table],
    top_k=10,
    # 在结果中过滤"时效性标记: 过时"的内容
)
```

## 当前建议（立即实施）

### 短期方案（1-2周内）

1. **增强保存逻辑**
   - 添加过期时间计算
   - 添加时效性标记
   - 记录保存时间和类型

2. **增强检索逻辑**
   - 检索时过滤过时内容
   - 优先返回新鲜内容
   - 在搜索结果中标注时效性

### 中期方案（1个月内）

3. **监控知识库增长**
   - 记录每日新增数量
   - 检索性能监控
   - 存储容量预警

4. **咨询SDK能力**
   - 确认是否有删除API
   - 确认容量限制
   - 了解官方推荐策略

### 长期方案（3个月内）

5. **实现自动清理**
   - 如果有删除API：实现过期清理服务
   - 如果无删除API：采用多知识库轮换策略

## 配置建议

```python
# config/knowledge_retention.json
{
    "retention_policy": {
        "行业趋势": 180,  # 天数
        "技术案例": 365,
        "用户洞察": 365,
        "项目经验": -1,   # 永久保留
        "竞品分析": 90
    },
    "quality_threshold": {
        "min_confidence": 0.7,  # 最低置信度
        "min_similarity": 0.85  # 去重阈值
    },
    "cleanup_schedule": {
        "enabled": true,
        "cron": "0 2 * * 0"  # 每周日凌晨2点清理
    }
}
```

## 监控指标

| 指标 | 目标值 | 告警阈值 |
|-----|-------|---------|
| 知识总数 | < 1000条 | > 2000条 |
| 平均检索时间 | < 500ms | > 1000ms |
| 过期知识占比 | < 20% | > 30% |
| 低质量知识占比 | < 5% | > 10% |
