# 开发环境配置

单进程 Python 应用，运行入口统一在仓库根目录。

## 组件清单

| 组件 | 版本 | 获取方式 |
| --- | --- | --- |
| Windows | 11 x64 | — |
| uv | 0.9 及以上 | `winget install Astral-sh.uv` |
| Python | 3.12 / 3.13 | 由 uv 下载并托管，无需手工安装 |
| Ollama | 可选 | 仅需要本地模型时安装，见 [ollama.md](ollama.md) |

不需要 Visual Studio、CMake、Ninja 或 vcpkg。

## Python 版本

`pyproject.toml` 中声明 `requires-python = ">=3.12,<3.14"`。uv 会挑一个满足条件的解释器下载到自己管理的目录，与机器上其他 Python 安装互不影响，因此本机的 miniconda、系统 Python 都不会被使用。

需要固定解释器时可显式安装：

```shell
uv python install 3.13
```

`uv.lock` 入库，锁定全部依赖的精确版本；`uv sync` 依据它重建环境。

## 安装步骤

### 1. 安装 uv

```shell
winget install Astral-sh.uv
```

### 2. 安装依赖

```shell
uv sync
```

首次执行会下载托管解释器与全部依赖，并创建 `.venv`。

### 3. 配置端点

```shell
Copy-Item .env.example .env
```

`.env` 已被 `.gitignore` 排除，不会入库。

## 配置项

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `SCISCITOR_BASE_URL` | `http://127.0.0.1:11434/v1` | OpenAI 兼容端点，必须带 `/v1` 前缀 |
| `SCISCITOR_API_KEY` | `ollama` | 本地服务忽略该值，但客户端要求非空 |
| `SCISCITOR_MODEL` | `qwen3:14b` | 发送请求时使用的模型名 |

环境变量优先于 `.env`，临时切换服务时不必修改文件。

## 验证安装

```shell
uv run ruff check     # 静态检查
uv run pytest         # 流式与配置的冒烟测试
uv run sciscitor      # 启动窗口
```

## 已知问题

**启动时提示 `module "QtQuick.Controls" is not installed`**

`PySide6-Essentials` 应当包含该 QML 模块。若当前版本未提供，装完整包即可：

```shell
uv add pyside6
```

**发送后报连接失败**

端点不可达。确认 Ollama 正在运行，或 `SCISCITOR_BASE_URL` 指向的服务可用；地址缺少 `/v1` 也会失败，因为客户端走 OpenAI 兼容协议。

**改了 `.env` 但没生效**

同名环境变量会覆盖 `.env`。用 `$env:SCISCITOR_BASE_URL` 检查当前 shell 中的值。
