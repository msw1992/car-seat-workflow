## 项目概述
- **名称**: 汽车座椅产品规划每日资讯推送工作流
- **功能**: 每日自动搜索汽车座椅领域最新资讯，通过AI分析生成产品规划建议，并推送到飞书群
- **支持**: 完全自动化定时推送（无需人工干预）

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| search_node | `nodes/search_node.py` | task | 搜索汽车座椅产品规划相关资讯 | - | - |
| knowledge_search_node | `nodes/knowledge_search_node.py` | task | 从Coze长期记忆库检索相关知识 | - | - |
| analysis_node | `nodes/analysis_node.py` | agent | 结合网络资讯和知识库内容，生成产品规划建议 | - | `config/seat_analysis_llm_cfg.json` |
| feishu_push_node | `nodes/feishu_push_node.py` | task | 将分析结果推送到飞书群 | - | - |
| save_knowledge_node | `nodes/save_knowledge_node.py` | task | 智能筛选并保存高价值内容到知识库 | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
无子图

## 智能知识保存功能

### 保存原则
工作流会自动判断分析结果是否值得保存到知识库：

**✅ 自动保存：**
- ✅ 重要的行业趋势报告
- ✅ 创新技术案例分析
- ✅ 用户需求洞察总结
- ✅ 成功/失败的项目经验
- ✅ 竞品分析报告

**❌ 自动跳过：**
- ❌ 日常新闻资讯（时效性短）
- ❌ 重复或相似内容（相似度>0.85）
- ❌ 低质量或未验证的信息
- ❌ 与座椅无关的内容

### 保存机制
1. **AI评估**：使用LLM判断内容的知识价值
2. **相似度检测**：检查知识库是否已有相似内容
3. **自动保存**：符合条件的内容自动添加到知识库

### 保存效果
- 知识库会自动积累高质量内容
- 避免重复和低质量信息
- 随着时间推移，知识库越来越完善
| 服务名 | 文件位置 | 功能描述 | 执行时间 |
|-------|---------|---------|---------|
| scheduler_service | `src/scheduler/scheduler_service.py` | 独立定时调度服务，自动触发工作流 | 每天8:30 |

### 定时服务配置
- **时区**: Asia/Shanghai (北京时间)
- **执行时间**: 每天 08:30 (可通过环境变量配置)
- **工作流API**: http://localhost:5000/run
- **日志位置**: /tmp/seat_push_scheduler.log

## 技能使用
- 节点`search_node`使用技能 web-search
- 节点`knowledge_search_node`使用技能 knowledge（引用知识库：Car_Seat）
- 节点`analysis_node`使用技能 llm
- 节点`feishu_push_node`使用技能 feishu-message
- 节点`save_knowledge_node`使用技能 llm + knowledge（保存到知识库：Car_Seat）

## 工作流程
```
搜索节点 → 知识库检索节点 → 分析节点 → 飞书推送节点 → 智能保存节点
```

### 执行步骤
1. **搜索节点**: 使用多个关键词搜索汽车座椅资讯
   - 关键词：产品规划、智能座舱、新材料、用户需求
   - **时间范围策略**：
     - 优先搜索最近一周的资讯
     - 如果结果不足20条，自动放宽到一个月
   - **时间过滤**：严格验证publish_time，过滤过期内容
   - 结果数量：20条
   - 详见 `docs/SEARCH_OPTIMIZATION_PLAN.md`
2. **知识库检索节点**: 从Coze长期记忆库检索相关知识
   - 当前知识库：Car_Seat_20260330_152242（新）
   - 检索数量：最多10条
   - 配置文件：data/knowledge_table.json
3. **分析节点**: 结合网络资讯和知识库内容，以座椅产品规划专家视角生成综合分析报告
4. **飞书推送节点**: 将分析结果以富文本形式推送到飞书群，标题包含当日日期
5. **智能保存节点**: 使用AI判断分析结果价值，自动保存高价值内容到知识库（避免重复）

### 知识库管理

**当前状态：**
- 当前知识库：Car_Seat_20260330_152242（2026-03-30创建）
- 旧知识库：Car_Seat（已废弃）
- 过期知识：0个
- 保留策略：详见 `docs/KNOWLEDGE_RETENTION_POLICY.md`

**重置知识库：**
```bash
# 查看重置计划
python scripts/reset_knowledge.py

# 执行重置（创建新知识库）
python scripts/reset_knowledge.py --execute
```

**配置管理：**
- 配置文件：`data/knowledge_table.json`
- 优先级：环境变量 > 配置文件 > 默认值
- 详见 `docs/KNOWLEDGE_RESET_GUIDE.md`

## 定时触发说明

### 方案一：使用独立定时服务（推荐）

**启动方式：**
```bash
# 1. 先启动工作流HTTP服务
python src/main.py -m http -p 5000 &

# 2. 启动定时调度服务
bash start_scheduler.sh
# 或直接运行
python src/scheduler/scheduler_service.py
```

**配置项（环境变量）：**
- `WORKFLOW_API_URL`: 工作流API地址（默认: http://localhost:5000/run）
- `SCHEDULE_HOUR`: 执行小时（默认: 8）
- `SCHEDULE_MINUTE`: 执行分钟（默认: 30）

**服务特点：**
- ✅ 完全自动化，无需人工干预
- ✅ 独立进程，不影响工作流主服务
- ✅ 自动重试，容错性强
- ✅ 完整日志记录

### 方案二：使用平台定时触发器
本工作流支持 Coze 平台自带的定时触发功能，在平台配置即可。

### 方案三：使用系统服务（生产环境推荐）
将定时服务配置为系统服务，开机自启动：
```bash
# 复制服务文件
sudo cp scripts/deploy_scheduler.sh /etc/systemd/system/seat-push.service

# 启用并启动服务
sudo systemctl enable seat-push
sudo systemctl start seat-push
```

## 输出内容
工作流会在飞书群推送包含以下内容的消息：
- 📈 今日趋势洞察
- 💡 创新方向建议（3-5个可落地的产品创新方向）
- 🔍 重点关注（AI技术与座椅结合应用）
- 📚 参考资料
