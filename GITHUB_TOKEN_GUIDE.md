
# GitHub Personal Access Token (PAT) 创建指南

## 🔑 创建 Token 步骤

### 方法 1: GitHub 网页创建 (推荐)

1. **访问 GitHub Token 设置页面**
   打开：https://github.com/settings/tokens

2. **点击 "Generate new token (classic)"**

3. **填写信息**
   - Note: `Quantitative Strategy MCP Deployment`
   - Expiration: `90 days` (或 No expiration)
   - Select scopes (勾选以下权限):
     ✅ repo (Full control of private repositories)
     ✅ workflow (Update GitHub Action workflows)
     ✅ write:packages (Upload packages to GitHub Package Registry)

4. **点击 "Generate token"**

5. **复制 Token**
   - Token 格式：`ghp_xxxxxxxxxxxxxxxxxxxx`
   - ⚠️ 只显示一次，务必复制保存！

### 方法 2: GitHub CLI (如果已安装)

```bash
gh auth token --scopes repo,workflow,write:packages
```

## 🔐 使用 Token 推送

创建好 Token 后，有 3 种使用方式：

### 方式 A: 直接在 URL 中使用 (简单但不推荐)
```bash
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/quantitative_strategy_mcp.git
```

### 方式 B: Git Credential Helper (推荐)
```bash
# 配置 Git 记住凭证
git config --global credential.helper store

# 推送时会提示输入用户名和 token
git push -u origin main
# Username: YOUR_USERNAME
# Password: 粘贴你的 token (不会显示)
```

### 方式 C: 环境变量 (最安全)
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
git remote add origin https://${GITHUB_TOKEN}@github.com/YOUR_USERNAME/quantitative_strategy_mcp.git
```

## ⚠️ 安全提醒

- ❌ 不要将 token 提交到代码仓库
- ❌ 不要将 token 发送到聊天或邮件
- ✅ 使用环境变量或 credential helper
- ✅ 定期更新 token
- ✅ 设置合适的过期时间

## 📞 下一步

创建好 token 后，请告诉我：
1. 你的 GitHub 用户名
2. 你的邮箱 (用于 git commit)
3. 你选择的认证方式 (A/B/C)

我会帮你完成剩余步骤！
