# 本地模型（可选）

Ollama 是**可选组件**。项目同时支持任意 OpenAI 兼容 API，不安装 Ollama 也能正常运行。

## 安装

```shell
winget install Ollama.Ollama
```

安装完成后 ollama 会作为后台服务常驻，默认监听 `127.0.0.1:11434`。

## 拉取模型

```shell
ollama pull qwen3:14b
```

模型体积较大，14B 量化版通常需要 9 GB 左右磁盘空间，运行时占用更多内存。机器内存有限时可以换用更小的型号，例如 `qwen3:7b`。

## 服务地址

```text
http://127.0.0.1:11434
```

默认只监听回环地址，不接受外部连接。

应用走 OpenAI 兼容协议，因此配置里必须用带 `/v1` 的地址，这一项已经是 `.env.example` 的默认值：

```text
SCISCITOR_BASE_URL=http://127.0.0.1:11434/v1
```

## 验证

```shell
curl http://127.0.0.1:11434/api/tags
```

能返回已安装模型的 JSON 列表即表示服务正常。
