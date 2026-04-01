# Coze OAuth 应用配置指南

## 概述

本指南帮助你在 Coze 平台创建 OAuth 应用，获取 API 凭证，从而在 GitHub Actions 中独立运行工作流，**不再依赖沙箱环境**。

## 两种应用类型对比

| 应用类型 | 认证方式 | GitHub Secrets 配置 |
|---------|---------|---------------------|
| **Web 后端应用** | Client ID + Client Secret | `COZE_CLIENT_ID` + `COZE_CLIENT_SECRET` |
| **服务类应用** ⭐ | Client ID + Private Key | `COZE_CLIENT_ID` + `COZE_PRIVATE_KEY` |

**推荐**：选择 **服务类应用**（更适合 GitHub Actions 这类纯后端场景）

---

## 方式一：服务类应用（推荐）

### 1. 创建应用

1. 登录 [Coze 平台](https://www.coze.cn)
2. 进入 **开发者中心** → **授权** → **创建应用**
3. 填写基本信息：
   - 应用类型：**普通**
   - 客户端类型：**服务类应用** ⭐
4. 点击 **创建并继续**

### 2. 获取凭证

在「配置」步骤中：

1. **Client ID** - 在应用信息中可见
2. **生成公钥/私钥** - 点击右上角 **「+ 创建 Key」**
   - 私钥会下载到本地（记得保存！）
   - 公钥会自动关联到应用

### 3. 复制私钥内容

```bash
# 查看私钥文件内容
cat downloaded_private_key.pem

# 或将私钥内容设置为环境变量
export COZE_PRIVATE_KEY="$(cat downloaded_private_key.pem)"
```

**注意**：私钥内容是多行文本，需要完整复制。

### 4. GitHub Secrets 配置

| Secret 名称 | 值 |
|------------|-----|
| `COZE_CLIENT_ID` | 应用详情页中的 Client ID |
| `COZE_PRIVATE_KEY` | 私钥文件的完整内容（多行） |
| `COZE_WORKSPACE_ID` | Coze 工作空间 ID |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL |
| `KNOWLEDGE_TABLE_NAME` | 知识库名称 |

**配置 Private Key 时的注意事项**：
- 私钥内容是多行文本，在 GitHub Secret 中输入时需要保持格式
- 确保包含 `-----BEGIN PRIVATE KEY-----` 和 `-----END PRIVATE KEY-----`
- 可以在终端中用 `cat private_key.pem | pbcopy` 复制

---

## 方式二：Web 后端应用

### 1. 创建应用

1. 登录 [Coze 平台](https://www.coze.cn)
2. 进入 **开发者中心** → **授权** → **创建应用**
3. 填写基本信息：
   - 应用类型：**普通**
   - 客户端类型：**Web 后端应用**
4. 点击 **创建并继续**

### 2. 获取凭证

在「配置」步骤中，你会直接获得：
- **Client ID**
- **Client Secret**（记得保存，只显示一次）

### 3. GitHub Secrets 配置

| Secret 名称 | 值 |
|------------|-----|
| `COZE_CLIENT_ID` | Client ID |
| `COZE_CLIENT_SECRET` | Client Secret |
| `COZE_WORKSPACE_ID` | Coze 工作空间 ID |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL |
| `KNOWLEDGE_TABLE_NAME` | 知识库名称 |

---

## 工作流程

```
GitHub Actions 触发
        │
        ▼
┌───────────────────────────────┐
│  检查认证配置                  │
│  (优先私钥 > Client Secret)  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│  调用 Token 端点获取 Access    │
│  Token (JWT 断言或 Basic Auth) │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│  设置 COZE_WORKLOAD_...       │
│  环境变量                      │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│  运行主工作流                  │
│  (搜索→分析→推送)             │
└───────────────────────────────┘
```

## 定时任务

workflow 已配置为每天 **北京时间 9:00** 自动运行：

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 1:00 = 北京时间 9:00
```

## 常见问题

### Q1: 服务类应用没有 Client Secret？

正常！服务类应用使用 **公钥/私钥** 替代 Client Secret 进行认证。

### Q2: 私钥格式是什么样的？

私钥文件应该以 `-----BEGIN PRIVATE KEY-----` 开头，例如：

```
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgE...
...（多行 base64 编码内容）...
-----END PRIVATE KEY-----
```

### Q3: GitHub Secret 中如何设置多行私钥？

在 GitHub 网页上添加 Secret 时：
1. 点击 **New repository secret**
2. Name 输入 `COZE_PRIVATE_KEY`
3. Value 区域需要粘贴私钥的**完整内容**（包括 `-----BEGIN...` 和 `-----END...`）

如果直接在终端设置：
```bash
# 使用单行（所有换行符用 \n 表示）
gh secret set COZE_PRIVATE_KEY --body "$(cat key.pem | tr '\n' ' ')"

# 或者使用文件
gh secret set COZE_PRIVATE_KEY < key.pem
```

### Q4: 可以同时配置多种认证方式吗？

可以！workflow 会按优先级自动选择：
1. `COZE_CLIENT_ID` + `COZE_PRIVATE_KEY` (优先)
2. `COZE_CLIENT_ID` + `COZE_CLIENT_SECRET`
3. `COZE_API_KEY` (PAT，降级)

### Q5: 获取 Token 失败？

1. 检查 Client ID 是否正确
2. 确认私钥与应用已正确关联
3. 检查应用是否已激活
4. 查看 GitHub Actions 日志中的具体错误信息

## 验证配置

手动触发 workflow 后，检查日志：

1. 如果看到 `使用 Private Key JWT 认证...`，说明正在使用私钥认证
2. 如果看到 `Token 获取成功！`，说明认证正常
3. 后续工作流节点正常运行
