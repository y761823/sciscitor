# sciscitor

基于 PySide6 + langchain 构建的 Windows 桌面 AI 客户端，单进程运行。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 界面 | PySide6（Qt Quick / QML） |
| 异步 | qasync（asyncio 与 Qt 事件循环共用） |
| 模型 | langchain-core + langchain-openai，任意 OpenAI 兼容端点 |
| 依赖管理 | uv（Python 解释器也由 uv 托管） |

## 环境要求

| 组件 | 版本 | 获取方式 |
| --- | --- | --- |
| Windows | 11 x64 | — |
| uv | 0.9 及以上 | `winget install Astral-sh.uv` |
| Python | 3.12 / 3.13 | 无需手工安装，`uv sync` 自动下载并托管 |
| 模型后端 | 任一 | 本地 Ollama（可选，见 [docs/ollama.md](docs/ollama.md)）或任意 OpenAI 兼容 API |

组件清单与常见问题见 [docs/environment.md](docs/environment.md)。

## 运行

```shell
uv sync
Copy-Item .env.example .env
uv run sciscitor
```

`.env` 默认指向本机 Ollama；对接其他服务时修改 `SCISCITOR_BASE_URL`、`SCISCITOR_API_KEY`、`SCISCITOR_MODEL`，环境变量优先于 `.env`。

界面上的 Model 输入框会预填 `SCISCITOR_MODEL`，可以在发送前临时改名。发送期间按钮变为 Stop，点击即中断请求，已经输出的内容保留在窗口里。

## 开发

```shell
uv run ruff check
uv run ruff format
uv run pytest
```
