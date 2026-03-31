# ✅ GitHub Actions 配置完成清单

> **只需要配置 Repository secrets（不需要 Environment secrets）**

---

## 📋 配置位置

```
GitHub 仓库 → Settings → Secrets and variables → Actions → Repository secrets
```

---

## ✅ 必需的 5 个 Secrets

### 1. COZE_API_KEY ⭐

**状态：** ✅ 已配置正确

**值：** `pat_tPcqlwBpsKl9cK2sEBUgOosDDKtqUSC9xDocEvrHL81Vspni8caW4WWF7R9HA3SL`

**验证结果：**
- ✅ 格式正确（pat_ 前缀）
- ✅ 长度正确（68 字符）
- ✅ API 调用成功

---

### 2. COZE_WORKLOAD_IDENTITY_API_KEY ⭐

**值：** **与 COZE_API_KEY 完全相同**

```
pat_tPcqlwBpsKl9cK2sEBUgOosDDKtqUSC9xDocEvrHL81Vspni8caW4WWF7R9HA3SL
```

---

### 3. COZE_WORKSPACE_ID ⭐⭐⭐ **关键**

**如何获取：**

```
步骤 1：访问 Coze 平台
https://www.coze.cn

步骤 2：进入您的 workspace
点击左上角的 workspace 名称

步骤 3：查看浏览器 URL
URL 格式：https://www.coze.cn/workspace/12345678
                                        ^^^^^^^^
                                        这就是 Workspace ID

步骤 4：复制并配置到 GitHub Secrets
Name: COZE_WORKSPACE_ID
Value: 12345678 (您的实际 ID)
```

**示例：**
```
如果您的 URL 是：
https://www.coze.cn/workspace/7123456890123456789

那么 Workspace ID 是：
7123456890123456789
```

---

### 4. FEISHU_WEBHOOK_URL

**如何获取：**

```
步骤 1：打开飞书群聊
进入要接收推送的飞书群

步骤 2：添加机器人
群设置 → 群机器人 → 添加机器人 → 自定义机器人

步骤 3：复制 Webhook 地址
格式：https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx-xxxxx-xxxxx

步骤 4：配置到 GitHub Secrets
Name: FEISHU_WEBHOOK_URL
Value: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
```

---

### 5. KNOWLEDGE_TABLE_NAME

**值：** `Car_Seat_20260330_152242`

**说明：** 这是您在 Coze 平台创建的知识库名称

---

## 🎯 配置步骤总结

1. **访问 Secrets 页面**
   ```
   GitHub 仓库 → Settings → Secrets and variables → Actions
   ```

2. **点击 "New repository secret"**

3. **逐个添加以下 5 个 secrets：**

   | Secret名称 | 值 |
   |-----------|---|
   | `COZE_API_KEY` | `pat_tPcqlwBpsKl9...` |
   | `COZE_WORKLOAD_IDENTITY_API_KEY` | `pat_tPcqlwBpsKl9...` (相同) |
   | `COZE_WORKSPACE_ID` | `您的 workspace ID` |
   | `FEISHU_WEBHOOK_URL` | `https://open.feishu.cn/...` |
   | `KNOWLEDGE_TABLE_NAME` | `Car_Seat_20260330_152242` |

4. **验证配置**
   ```
   Actions → Run workflow → 查看日志中的 "验证环境变量配置" 步骤
   ```

---

## ⚠️ 常见错误

### 错误 1：缺少 COZE_WORKSPACE_ID

**现象：**
```
[WARNING] workspace_id is required
```

**解决：** 按照上面的步骤获取并配置 COZE_WORKSPACE_ID

### 错误 2：COZE_WORKLOAD_IDENTITY_API_KEY 与 COZE_API_KEY 不同

**解决：** 确保这两个 secrets 的值完全相同

### 错误 3：FEISHU_WEBHOOK_URL 格式错误

**解决：** 确保以 `https://open.feishu.cn/` 开头

---

## ✅ 验证方法

配置完成后，运行 workflow，检查日志：

```
✅ COZE_API_KEY 格式正确
✅ COZE_WORKSPACE_ID 已配置: 12345678
✅ COZE_WORKLOAD_IDENTITY_API_KEY 已配置
✅ FEISHU_WEBHOOK_URL 已配置
✅ KNOWLEDGE_TABLE_NAME 已配置
✅ 所有环境变量配置正确！
```

---

## 📸 配置示例截图

```
┌─────────────────────────────────────────────────┐
│ Repository secrets                               │
├─────────────────────────────────────────────────┤
│ COZE_API_KEY                          [Update]  │
│ COZE_WORKLOAD_IDENTITY_API_KEY        [Update]  │
│ COZE_WORKSPACE_ID                     [Update]  │
│ FEISHU_WEBHOOK_URL                    [Update]  │
│ KNOWLEDGE_TABLE_NAME                  [Update]  │
│                                                  │
│ [New repository secret]                          │
└─────────────────────────────────────────────────┘
```

---

## 🚀 完成后

1. **测试运行**
   ```
   Actions → daily_push → Run workflow → Run workflow
   ```

2. **查看日志**
   - 搜索节点：搜索汽车座椅资讯
   - 知识库节点：检索相关知识
   - 分析节点：生成分析报告
   - 推送节点：发送到飞书

3. **检查飞书**
   - 查看是否收到推送消息
