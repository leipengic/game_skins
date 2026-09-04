# 贡献指南

欢迎提交 Issue / Pull Request。

## 本地开发

```bash
git clone <repo-url> game_skins
cd game_skins
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

## 提 PR 前

```bash
# 1. 跑测试
pytest tests/ -v

# 2. lint
flake8 _common lol kpl overwatch tests --max-line-length=100

# 3. 格式化（保存后）
black _common lol kpl overwatch tests
isort _common lol kpl overwatch tests
```

## 新增子包

如果要新增游戏（例如守望先锋）的下载器，按以下步骤：

1. 在根目录建 `overwatch/`（已建好占位）
2. 在 `overwatch/__init__.py` 里加注释
3. 写主脚本 `overwatch/<your>.py`
4. 复用 `_common/`：
   - `request_with_retry(url, ...)` —— HTTP GET + 重试
   - `download_image(url, save_path, ...)` —— 落盘
   - `sanitize_filename(name)` —— 文件名清理
   - `add_common_download_args(parser)` —— CLI 标准化
5. 加 `overwatch/README.md` 说明数据源与参数
6. 在 `requirements.txt` 加本子包特有的依赖
8. 在 tests 里加关键路径的单元测试

## 数据源合规

- **不要**绕过反爬措施（如验证码、IP 限制、robots.txt 显式禁止）
- README 必须明示"仅供学习交流"+"图片版权归原厂商所有"
- 加 `--delay` 限速，避免给数据源造成压力