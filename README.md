# OICC

OICC 是正在开发的 OIOIC 节点与构造代码生成工具，使用 C11 和 OIOIC 对象模型实现。目标是读取节点继承声明，生成面向当前 OIOIC API 的 C 构造代码，并提供节点骨架创建能力。

目前已实现节点骨架创建、C 注释标记解析、继承校验、构造区预览/更新和自举再生，并提供生成代码运行及失败清理回归。首次构建不需要其他仓库、旧 oicc 二进制或联网下载依赖。命令、支持语法与一致性边界见 [oicc 使用说明](docs/oicc.md)。

## 构建参考程序

安装 xmake 和 C11 工具链。Windows 使用完整 MinGW-w64，并将其工具加入 PATH；在仓库根目录运行：

```sh
xmake f -P . -p mingw -m debug
xmake -P . oioic_reference
xmake run -P . oioic_reference
```

Linux 可将配置命令替换为 `xmake f -P . --toolchain=gcc -m debug`。详细流程与实际验证边界见 [构建说明](docs/build.md)。默认 `xmake -P .` 构建 oicc 及 OIOIC 静态库；参考程序需要显式选择。

```sh
xmake -P . oicc
xmake run -P . oicc --help
python tests/test_oicc.py --oicc build/mingw/x86_64/debug/oicc.exe
```

## 项目资料

- [开发指南与拟定架构](AGENTS.md)
- [OIOIC 模型与生成契约](docs/oioic-reference.md)
- [本地依赖来源](third_party/oioic/README.md)
- [继承参考示例](examples/oioic_reference/README.md)
- [第三方声明](THIRD_PARTY_NOTICES.md)

源码与必要生成代码纳入 Git，构建缓存和机器设置由忽略规则排除。所有依赖源码随仓库提供，目录引用均相对于仓库，便于其他开发者独立阅读和构建。

## 许可证

项目使用 [MIT License](LICENSE)。OIOIC 运行时与摘选示例保留其原有版权和 MIT 许可，详见 [第三方声明](THIRD_PARTY_NOTICES.md)。
