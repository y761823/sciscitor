# 开发环境配置

本项目由 C++（Qt 客户端）与 Go（服务端）两部分组成，构建入口统一在仓库根目录。

## 组件清单

| 组件 | 版本 | 获取方式 |
| --- | --- | --- |
| Windows | 11 x64 | — |
| Visual Studio | 2022（MSVC v143） | 手工安装，勾选「使用 C++ 的桌面开发」 |
| Qt | 6.12（msvc2022_64） | Qt Online Installer |
| Go | 1.25 | 由 mise 安装 |
| CMake | 3.27+ | `bootstrap.ps1` |
| Ninja | 任意 | `bootstrap.ps1` |
| vcpkg | 可选 | 仅当 `vcpkg.json` 声明了 C++ 依赖时需要 |

## 安装步骤

### 1. 自动安装工具链

在 PowerShell 中执行（需要 winget）：

```powershell
scripts/bootstrap.ps1
```

会安装 mise、CMake、Ninja，然后执行 `mise install` 拉取 `mise.toml` 中锁定的 Go 版本。

### 2. 手动安装

`bootstrap.ps1` 不处理任何机器相关的路径，以下需要手工完成。

**Qt 6.12**：用 Qt Online Installer 安装，组件勾选 `MSVC 2022 64-bit`，或更新版本。

**vcpkg**（可选）：

```shell
git clone https://github.com/microsoft/vcpkg <vcpkg 目录>
<vcpkg 目录>\bootstrap-vcpkg.bat
```

### 3. 生成本机 CMake 预设

```powershell
Copy-Item CMakeUserPresets.json.example CMakeUserPresets.json
```

然后把两个路径改成自己机器上的实际位置：

```json
{
  "cacheVariables": {
    "CMAKE_PREFIX_PATH": "<Qt 安装目录>/6.12.0/msvc2022_64",
    "CMAKE_TOOLCHAIN_FILE": "<vcpkg 目录>/scripts/buildsystems/vcpkg.cmake"
  }
}
```

JSON 中请使用正斜杠。`CMakeUserPresets.json` 已被 `.gitignore` 忽略，不会进入仓库。

## 路径约定

机器相关的路径只出现在两处，且必须保持一致：

| 路径 | 由谁设置 | 需要同步到 |
| --- | --- | --- |
| Qt 安装目录 | Qt Online Installer | `CMakeUserPresets.json` 的 `CMAKE_PREFIX_PATH` |
| vcpkg 目录 | 手工 clone | `CMakeUserPresets.json` 的 `CMAKE_TOOLCHAIN_FILE` |

`CMakePresets.json` 不含任何绝对路径，可直接共享；`bootstrap.ps1` 同样不含路径。

## 配置文件归属

| 内容 | 配置文件 | 是否入库 | 说明 |
| --- | --- | --- | --- |
| Go 版本 | `mise.toml` | 是 | 由 mise 注入 PATH |
| C++ 依赖 | `vcpkg.json` | 是 | manifest 模式，锁定依赖与 baseline |
| 通用构建配置 | `CMakePresets.json` | 是 | 不含机器路径，可直接共享 |
| 本机路径 | `CMakeUserPresets.json` | 否 | Qt / vcpkg 位置 |

不同项目互不影响；机器相关路径只存在于不入库的 `CMakeUserPresets.json` 中。

## 验证安装

```shell
cmake --list-presets          # 应列出 local-debug / local-release 等预设
cmake --preset local-debug    # 应无报错完成配置
cmake --build --preset local-debug
```

构建成功后会得到两个产物：

- `build/local-debug/client/appSciscitorClient.exe`
- `build/local-debug/bin/sciscitor-server.exe`

## 已知问题

**CMake 找不到 go**

mise 通过 shell hook（`mise activate`）注入 PATH，只有交互式终端里才生效。从开始菜单启动的 Qt Creator、CI、计划任务等进程看不到 go。

`server/CMakeLists.txt` 已内置回退：找不到 `go` 时改用 `mise exec -- go`。若仍失败，确认 `mise` 本身在 PATH 中。

**configure 时提示 Qt6QmlAssetDownloaderPrivate 找不到**

该模块依赖 QtTaskTree，属实验性的 `Qt.labs.assetdownloader`，与 Quick / Controls 无关，可忽略。需要消除警告时用 Qt Maintenance Tool 补装 QtTaskTree。

**Invalid configure preset: "local": Could not find inherited preset "windows"**

`CMakeUserPresets.json` 的 `inherits` 指向 `CMakePresets.json` 中定义的隐藏基类。请确认构建时的工作目录是仓库根目录，而不是 `client/` 或 `server/`。
