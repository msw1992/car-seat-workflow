# Coze OAuth 应用配置指南

## 概述

本指南帮助你在 Coze 平台创建 OAuth 应用，获取 `client_id` 和 `client_secret`，从而在 GitHub Actions 中独立运行工作流，**不再依赖沙箱环境**。

## 为什么需要 OAuth 应用？

- 沙箱环境的 Token 有时效性，断开后会导致 GitHub Actions 无法运行
- 使用自己的 OAuth 应用，Token 由你自己控制
- 支持在 GitHub Actions 中自动获取 Token，无需手动管理

## 创建步骤

### 1. 登录 Coze 平台

访问 [https://www.coze.cn](https://www.coze.cn) 并登录你的账号。

### 2. 进入开发者设置

1. 点击右上角头像
2. 选择 **"开放平台"** 或 **"开发者中心"**
3. 找到 **"OAuth 应用"** 或 **"应用管理"**

### 3. 创建 OAuth 应用

1. 点击 **"创建应用"**
2. 选择应用类型：**服务端应用 (Server-side App)**
3. 填写应用信息：
   - 应用名称：`GitHub Actions Token`
   - 应用描述：`用于 GitHub Actions 自动获取 API Token`
4. 完成创建

### 4. 获取凭证

创建应用后，你会获得：
- **Client ID**：应用的唯一标识
- **Client Secret**：应用密钥

**重要**：Client Secret 只显示一次，请妥善保存！

### 5. 配置应用权限

确保应用有权限访问：
- 知识库 API
- LLM API
- 搜索 API

### 6. 获取 Workspace ID

如果尚未获取：

1. 在 Coze 平台进入你的工作空间
2. 点击 **"设置"** 或 **"工作空间设置"**
3. 找到 **Workspace ID**（通常是一串数字）

## GitHub Secrets 配置

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中添加以下 Secrets：

### 方式一：OAuth 凭证（推荐）

| Secret 名称 | 说明 | 示例值 |
|-----------|------|-------|
| `COZE_CLIENT_ID` | OAuth 应用 Client ID | `dmplxxxxxxxxxx` |
| `COZE_CLIENT_SECRET` | OAuth 应用 Client Secret | `MwJ8Rx...` |
| `COZE_WORKSPACE_ID` | Coze 工作空间 ID | `123456789` |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL | `https://open.feishu.cn/...` |
| `KNOWLEDGE_TABLE_NAME` | 知识库名称 | `汽车座椅知识库` |

### 方式二：直接使用 PAT（如果 Coze 支持）

| Secret 名称 | 说明 | 示例值 |
|-----------|------|-------|
| `COZE_API_KEY` | Personal Access Token | `pat_xxxxxxxxxx` |
| `COZE_WORKSPACE_ID` | Coze 工作空间 ID | `123456789` |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL | `https://open.feishu.cn/...` |
| `KNOWLEDGE_TABLE_NAME` | 知识库名称 | `汽车座椅知识库` |

## 工作流程

```
GitHub Actions 触发
        │
        ▼
┌───────────────────────┐
│  检查 COZE_CLIENT_ID  │
│  和 COZE_CLIENT_SECRET│
└───────────┬───────────┘
            │
            ▼ (如果配置了 OAuth)
┌───────────────────────┐
│  调用 OAuth Token     │
│  端点获取 Access Token│
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  设置环境变量         │
│  COZE_WORKLOAD_...    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  运行主工作流         │
│  (搜索→分析→推送)     │
└───────────────────────┘
```

## 定时任务

workflow 已配置为每天 **北京时间 9:00** 自动运行：

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 1:00 = 北京时间 9:00
```

## 常见问题

### Q1: OAuth 应用创建失败？

检查是否具有创建应用的权限。可能需要企业版或特定的开发者权限。

### Q2: 获取 Token 失败？

1. 检查 Client ID 和 Client Secret 是否正确
2. 确认 OAuth 应用已激活
3. 检查应用权限是否足够

### Q3: 可以同时配置 OAuth 和 PAT 吗？

可以！workflow 会优先使用 OAuth 凭证，如果 OAuth 凭证缺失，则降级使用 PAT。

### Q4: Token 会过期吗？

OAuth Access Token 有效期通常为 **24 小时**。workflow 每次运行前会自动获取新 Token，所以无需担心过期问题。

## 验证配置

手动触发 workflow 后，检查日志：

1. 如果看到 `使用 OAuth 方式获取 Token...`，说明正在使用 OAuth
2. 如果看到 `Token 获取成功！`，说明 Token 获取正常
3. 后续工作流节点正常运行

## 安全建议

1. **不要泄露 Client Secret**：它是应用的密码，只能你自己知道
2. **定期轮换**：建议每隔几个月更新 Client Secret
3. **最小权限**：只授予应用必要的 API 权限
