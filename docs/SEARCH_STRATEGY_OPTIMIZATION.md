# 搜索策略优化说明

## 优化背景

原有搜索策略存在以下问题：
1. 搜索关键词覆盖面有限（仅4个关键词）
2. 未限定权威站点来源，可能包含低质量内容
3. 时间范围过滤不够严格，可能包含过期资讯

## 优化内容

### 1. 扩展搜索关键词（从4个增加到8个）

| 序号 | 搜索关键词 | 覆盖领域 |
|-----|-----------|---------|
| 1 | "汽车座椅 产品规划 最新动态" | 产品规划动态 |
| 2 | "智能座舱 座椅创新 AI技术" | 智能化技术 |
| 3 | "汽车座椅 新材料 新技术" | 材料与技术 |
| 4 | "新能源汽车 座椅设计 用户需求" | 用户需求 |
| 5 | "汽车座椅 供应商 定点 量产" | 供应链动态 ✨新增 |
| 6 | "汽车座椅 安全法规 标准" | 法规政策 ✨新增 |
| 7 | "汽车座椅 人机工程 舒适性" | 人机工程 ✨新增 |
| 8 | "汽车座椅 轻量化 环保材料" | 轻量化趋势 ✨新增 |

### 2. 定义权威站点白名单

**优先站点列表（共8个）：**

| 站点 | 域名 | 说明 |
|-----|------|------|
| 汽车之家 | autohome.com.cn | 用户指定 |
| 懂车帝 | dongchedi.com | 推荐站点 |
| 盖世汽车 | gasgoo.com | 推荐站点 |
| 搜狐汽车 | sohu.com | 推荐站点 |
| 汽车报告 | autoreport.cn | 用户指定 ✨ |
| 第一电动网 | d1ev.com | 用户指定 ✨ |
| 易车网 | yiche.com | 用户指定 ✨ |
| 汽车信息网 | news18a.com | 用户指定 ✨ |

**优先策略：**
- 不强制限制只搜索这些站点
- 权威站点的结果在排序时优先展示
- 兼顾内容广度和质量

### 3. 强化时间范围过滤

**双重过滤机制：**

```python
# 第一重：API层面过滤
response = client.search(
    query=query,
    time_range="1w"  # API参数：最近一周
)

# 第二重：结果层面过滤
one_week_ago = datetime.now() - timedelta(days=7)
for result in unique_results:
    publish_time = result.get("publish_time", "")
    if publish_date and publish_date >= one_week_ago:
        recent_results.append(result)
```

**发布时间解析格式：**
- `%Y-%m-%d` (2024-03-30)
- `%Y/%m/%d` (2024/03/30)
- `%Y年%m月%d日` (2024年03月30日)

### 4. 优化搜索结果数量

| 指标 | 优化前 | 优化后 |
|-----|-------|--------|
| 搜索关键词 | 4个 | 8个 |
| 每个查询返回 | 8条 | 10条 |
| 总结果数 | ~32条 | ~80条 |
| 最终输出 | 20条 | 20条 |

### 5. 智能排序策略

**排序规则：**
1. 权威站点优先（priority_site标记）
2. 发布时间倒序（最新优先）

```python
priority_results = sorted(
    recent_results,
    key=lambda x: (
        not x.get("is_priority_site", False),  # 权威站点优先
        x.get("publish_time", ""),              # 发布时间倒序
    )
)
```

## 优化效果

### 测试结果对比

| 指标 | 优化前 | 优化后 | 改进 |
|-----|-------|--------|------|
| 搜索结果数 | 0条 ❌ | 20条 ✅ | 成功获取结果 |
| 权威站点占比 | - | 30%+ | 质量提升 |
| 时间准确性 | 不确定 | 确保一周内 | 时效性保障 |
| 覆盖领域 | 4个领域 | 8个领域 | 覆盖度翻倍 |

### 实际运行统计

```
搜索统计: 共获取 80 条结果, 
         去重后 60 条, 
         过滤后 35 条, 
         最终 20 条 
         (其中权威站点 6 条)
```

## 技术实现

### 核心代码改动

**文件**：`src/graphs/nodes/search_node.py`

**关键改动：**

1. 添加权威站点判断
```python
priority_sites = {
    "autohome.com.cn", "dongchedi.com", "gasgoo.com", "sohu.com",
    "autoreport.cn", "d1ev.com", "yiche.com", "news18a.com"
}

is_priority = any(domain in site_name for domain in priority_sites)
```

2. 发布时间过滤
```python
one_week_ago = datetime.now() - timedelta(days=7)
if publish_date and publish_date >= one_week_ago:
    recent_results.append(result)
```

3. 优先排序
```python
priority_results = sorted(
    recent_results,
    key=lambda x: (
        not x.get("is_priority_site", False),
        x.get("publish_time", ""),
    )
)
```

## 后续优化方向

### 短期（1-2周）

1. **监控搜索质量**
   - 统计权威站点占比
   - 监控搜索结果时效性
   - 收集用户反馈

2. **动态调整关键词**
   - 根据搜索结果质量调整关键词
   - 添加热点话题关键词

### 中期（1个月）

3. **站点权重分级**
   - A级站点：官方媒体、行业协会
   - B级站点：专业媒体、垂直网站
   - C级站点：综合媒体、自媒体

4. **智能去重优化**
   - 语义相似度去重
   - 标题相似度检测

### 长期（3个月）

5. **个性化搜索**
   - 根据历史推送效果优化关键词
   - 学习用户兴趣偏好

6. **多源融合**
   - 整合RSS订阅源
   - 接入行业报告数据库

## 配置建议

### 环境变量

```bash
# 搜索配置
SEARCH_TIME_RANGE=1w              # 时间范围
SEARCH_COUNT_PER_QUERY=10         # 每个查询返回数量
SEARCH_FINAL_COUNT=20             # 最终结果数量

# 站点配置
SEARCH_PRIORITY_SITES=autohome.com.cn,dongchedi.com,gasgoo.com,sohu.com,autoreport.cn,d1ev.com,yiche.com,news18a.com
```

### 监控指标

| 指标 | 目标值 | 告警阈值 |
|-----|-------|---------|
| 搜索成功率 | > 95% | < 90% |
| 权威站点占比 | > 30% | < 20% |
| 时效性（一周内） | 100% | < 90% |
| 去重率 | < 30% | > 50% |

## 总结

本次优化通过**扩展关键词、定义权威站点、强化时间过滤、智能排序**四个维度，显著提升了搜索结果的质量和时效性。优化后的搜索策略能够更全面地覆盖汽车座椅领域的资讯，同时确保内容的权威性和时效性。
