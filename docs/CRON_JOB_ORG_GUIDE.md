# 使用 cron-job.org 触发 GitHub Actions

## 概述

由于 GitHub Actions 的 `schedule` 功能不稳定，我们使用免费的 cron-job.org 来定时触发 workflow。

---

## 步骤 1：创建 GitHub Personal Access Token (PAT)

1. 访问 GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 直接链接：https://github.com/settings/tokens/new

2. 创建新 Token：
   - **Note**: `cron-job-trigger`
   - **Expiration**: No expiration（永不过期）
   - **Scopes**: 勾选 `repo`（完整仓库权限）

3. 点击 **Generate token**
4. **立即复制保存** Token（只显示一次！）

---

## 步骤 2：注册 cron-job.org

1. 访问 https://cron-job.org
2. 点击 **Sign up** 注册账号
3. 验证邮箱后登录

---

## 步骤 3：创建定时任务

1. 登录后点击 **Create cronjob**

2. 填写基本信息：
   - **Title**: `汽车座椅每日推送`
   - **URL**: 
     ```
     https://api.github.com/repos/msw1992/car-seat-workflow/dispatches
     ```
   - **Schedule**: 选择 **User defined**
   - **Cron expression**: `35 1 * * *` (每天 UTC 1:35 = 北京时间 9:35)

3. **Request settings**:
   - **HTTP method**: POST
   - **Headers** (每行一个):
     ```
     Authorization: token YOUR_GITHUB_PAT
     Content-Type: application/json
     ```
     > 替换 `YOUR_GITHUB_PAT` 为你在步骤 1 创建的 Token
   
   - **Request body**:
     ```json
     {"event_type": "daily-trigger"}
     ```

4. 点击 **Create cronjob**

---

## 步骤 4：测试

1. 在 cron-job.org 任务列表中，点击任务旁边的 **Run now** 按钮
2. 等待几分钟后检查 GitHub Actions 页面
3. 应该能看到新的 workflow 运行记录

---

## 调试信息

- **URL**: `https://api.github.com/repos/msw1992/car-seat-workflow/dispatches`
- **Method**: POST
- **Headers**:
  ```
  Authorization: token ghp_xxxxxxxxxxxx
  Content-Type: application/json
  ```
- **Body**:
  ```json
  {"event_type": "daily-trigger"}
  ```

---

## 常见问题

### Q: 任务执行了但 GitHub Actions 没运行？

检查：
1. PAT 是否有 `repo` 权限
2. Header 格式是否正确：`Authorization: token ghp_xxx`（注意 `token` 关键字）
3. Body 是否是有效的 JSON

### Q: 如何查看执行日志？

在 cron-job.org 任务详情页，可以看到每次执行的日志。

---

## 时间对照表

| 北京时间 | UTC 时间 | Cron 表达式 |
|---------|---------|------------|
| 9:35 | 1:35 | `35 1 * * *` |
| 9:00 | 1:00 | `0 1 * * *` |
| 18:00 | 10:00 | `0 10 * * *` |
