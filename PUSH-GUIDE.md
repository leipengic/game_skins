# game_skins 推送指南

本仓库已 `git init` + 首次 commit，等你在 GitHub 网页建仓后 push。

提交指纹：`0b08b479e1d7ac60416313972a8d9e6ee92f2c0b`（main 分支）

---

## 第 1 步：在 GitHub 创建空仓库

打开 <https://github.com/new>，按下面填：

| 字段 | 值 |
|---|---|
| Owner | `leipengic` |
| Repository name | `game_skins` |
| Description | `王者荣耀 / 英雄联盟 / 守望先锋（规划）英雄皮肤与壁纸批量下载工具集（Python monorepo）` |
| Visibility | **Public** |
| Initialize | ❌ **不要**勾选 Add a README file |
| Initialize | ❌ **不要**勾选 Add .gitignore |
| Initialize | ❌ **不要**勾选 Choose a license |

> ⚠️ 三个 Initialize 全部**取消**。本仓库已有 README/.gitignore/LICENSE，不能让 GitHub 模板覆盖。

点击 **Create repository**，会跳转到空仓库页面（显示 "Quick setup"）。

---

## 第 2 步：本地推送

打开 Git Bash（项目根目录 `H:\CloudMusic\2026-09-04-17-30-34\game_skins`），执行：

```bash
git remote add origin https://github.com/leipengic/game_skins.git
git push -u origin main
```

### 首次推送会弹凭证框

由于 GitHub 已禁用密码认证，第一次 push 会弹出 Windows 凭证对话框：

1. 用户名自动填 `leipengic`
2. 密码框粘贴 **Personal Access Token (PAT)** —— 不是 GitHub 登录密码
3. 点"确定"

> 💡 PAT 申请方式：GitHub → 右上头像 → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token。**至少勾选 `repo` 权限**。生成后**只显示一次**，复制保存。

推送成功后 Windows Credential Manager 会记住 PAT，后续 push 不再弹框。

### 验证

推送完成后访问 <https://github.com/leipengic/game_skins>，应看到：

- 29 个文件
- README 渲染正常（badge / 子包表格）
- `.github/workflows/lint.yml` 显示 ✓ 标签（CI 自动跑）

---

## 第 3 步：后续推送

```bash
git add -A
git commit -m "type: scope - description"
git push
```

---

## 备选：URL 嵌入 token（绕过弹框）

如果不想走 Windows Credential Manager，可以临时用嵌入 token 的 URL：

```bash
# 把 YOUR_TOKEN 换成你的 PAT
git remote set-url origin https://YOUR_TOKEN@github.com/leipengic/game_skins.git
git push -u origin main

# 推送成功后，强烈建议改回标准 URL，避免 token 写入 .git/config 后被误提交
git remote set-url origin https://github.com/leipengic/game_skins.git
```

> ⚠️ 如果用这个方式，**切记别把 `.git/config` 提交到公共仓库**——但本仓库 .git/config 在 .git/ 目录，不会被 git 跟踪，所以实际上风险极低。但建议改回标准 URL。

---

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `Repository not found` | 远程仓库名拼错 / 没建仓 | 检查 GitHub 网页是否已建 `game_skins` |
| `403 Forbidden` | PAT 没勾 `repo` 权限 | 重新生成 PAT，至少勾 `repo` |
| `SSL certificate problem` | 公司网络拦截 | 设 `git config http.sslVerify false`（仅临时） |
| `failed to push some refs` | 远程有 commit 你没有 | `git pull origin main --rebase` 后再 push |
| 弹框一直要密码 | 用了真密码 | 必须换 PAT；清掉旧凭证：`cmdkey /list` + `cmdkey /delete:git:https://github.com` |

---

## 推送成功后

1. 访问新仓确认无误
2. 处理老仓（见 `../game_skins-legacy-readmes/PUSH-GUIDE.md`）
3. CI 第一次会自动跑，约 1-2 分钟查看结果