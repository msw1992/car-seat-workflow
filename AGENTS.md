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
- **执行时间**: 每天 08:30 (已配置)
- **工作流API**: http://localhost:5000/run
- **日志位置**: /tmp/seat_push_scheduler.log

**⚠️ 重要：后台运行说明**

关闭网页/终端后，定时任务是否继续执行取决于启动方式：

| 启动方式 | 关闭网页后 | 推荐场景 |
|---------|-----------|---------|
| `bash start_scheduler.sh` | ❌ 会停止 | 临时测试 |
| `bash start_scheduler_daemon.sh` | ✅ 继续运行 | **生产环境推荐** |

**启动定时服务（后台运行）：**
```bash
# 1. 先启动工作流HTTP服务
python src/main.py -m http -p 5000 &

# 2. 启动定时调度服务（后台运行，关闭网页也不会停止）
bash start_scheduler_daemon.sh
```

**管理命令：**
```bash
# 查看服务状态
bash scripts/scheduler_status.sh

# 查看实时日志
tail -f /tmp/seat_push_scheduler.log

# 停止服务
bash scripts/stop_scheduler.sh

# 检查配置
python scripts/check_schedule.py
```

**修改执行时间：**
```bash
# 方式1：环境变量（临时）
export SCHEDULE_HOUR="9"
export SCHEDULE_MINUTE="00"

# 方式2：修改启动脚本（永久）
# 编辑 start_scheduler_daemon.sh，取消注释并修改环境变量
```

**查看配置状态：**
```bash
python scripts/check_schedule.py
```

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

### 🆓 免费部署方案（推荐）

#### 方案一：GitHub Actions（最推荐）⭐⭐⭐⭐⭐

**优势：**
- ✅ 完全免费（每月2000分钟额度）
- ✅ 零服务器维护
- ✅ 代码更新自动部署
- ✅ 支持手动触发测试

**快速部署（10分钟）：**
```bash
# 1. 推送代码到 GitHub
git add .
git commit -m "feat: 添加定时任务"
git push

# 2. 在 GitHub 网页配置 Secrets
Settings → Secrets → Actions → 添加环境变量

# 3. 启用 Actions
Actions → Enable workflows

# 4. 测试运行
Actions → Run workflow
```

**⚠️ 关键配置：COZE_API_KEY**

在 GitHub Actions 运行前，必须配置正确的 `COZE_API_KEY`：

| Secret名称 | 值 | 获取方式 |
|-----------|---|---------|
| `COZE_API_KEY` | `pat_xxxxx` | ⭐ **见详细文档** |
| `COZE_WORKLOAD_IDENTITY_API_KEY` | `pat_xxxxx` | **与上面相同** |
| `COZE_WORKSPACE_ID` | `12345678` | Coze平台 URL 获取 |
| `FEISHU_WEBHOOK_URL` | `https://...` | 飞书群机器人 |
| `KNOWLEDGE_TABLE_NAME` | `Car_Seat_xxx` | 知识库名称 |

**详细文档：**
- [快速开始指南](../QUICKSTART_GITHUB_ACTIONS.md)
- [COZE_API_KEY 获取指南](docs/COZE_API_KEY_GUIDE.md) ⭐ **最关键**
- [GitHub Secrets 配置清单](docs/GITHUB_SECRETS_CHECKLIST.md)
- [免费方案对比](docs/FREE_DEPLOYMENT_GUIDE.md)

**常见错误：**
```
❌ token contains an invalid number of segments
   → Token 格式错误，应以 pat_ 或 sat_ 开头

❌ authentication is invalid
   → Token 无效或过期，请重新创建
```

**诊断工具：**
```bash
# 本地验证 Token 格式
export COZE_API_KEY="您的token"
python scripts/diagnose_token.py
```

#### 方案二：云函数（阿里云/腾讯云）

**优势：**
- ✅ 每月100万次免费调用
- ✅ 无需管理服务器

**部署步骤：** 详见 `docs/FREE_DEPLOYMENT_GUIDE.md`

---

### 方案三：使用独立定时服务（沙箱环境）

**启动方式：**
```bash
# 1. 先启动工作流HTTP服务
python src/main.py -m http -p 5000 &

# 2. 启动定时调度服务
bash start_scheduler_daemon.sh  # 后台运行，关闭网页也不会停止
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
