# sciscitor

AI Desktop —— 基于 Qt6 + C++20 + Go 构建的 Windows AI 桌面应用。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| Client | Qt 6.12、QML、C++20 |
| Server | Go 1.25 |
| AI | Ollama、OpenAI Compatible API |
| Storage | SQLite |
| Build | CMake、vcpkg |
| Toolchain | mise |

## 环境配置

组件清单、安装步骤、路径约定与常见问题见 [docs/environment.md](docs/environment.md)。

首次使用需要完成三件事：安装工具链、安装 Qt 6.12、生成本机 `CMakeUserPresets.json`。

## 编译

一次构建同时产出 client 与 server：

```shell
cmake --preset local-release
cmake --build --preset local-release
```

产物：

- `build/local-release/client/appSciscitorClient.exe`
- `build/local-release/bin/sciscitor-server.exe`

调试时把 `local-release` 换成 `local-debug`。

### 只编译 Server

```shell
cd server
go build ./...
```

## 运行

1. 先启动 server
2. 然后启动 Qt Client

## 可选组件

本地模型推理通过 [Ollama](docs/ollama.md) 提供，属可选项；也可以直接使用任意 OpenAI 兼容 API。
