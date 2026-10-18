# OpenOICC

OpenOICC 是面向 [NEOioic](https://github.com/neoioic/neoioic) 的节点与构造代码生成工具，使用 C11 和 NEOioic 对象模型实现。它读取节点继承声明，生成面向当前 NEOioic API 的 C 构造代码，并提供节点骨架创建能力。正式名称写作 OpenOICC，命令、文件名和代码标识使用 `openoicc`，输入语法保留 `<oicc>` 标记。

NEOioic（代码标识 `neoioic`）由 OIOIC 发展而来，未来可能发生不兼容的 API 更新。OpenOICC 以仓库内固定的 NEOioic 版本为生成目标，随其契约演进，不承诺兼容历史 OIOIC 或任意未来版本。升级运行时时须同步检查生成模板、构造辅助代码和行为验证。

目前已实现 go/ao/co/ro/mo 分类骨架创建、C 注释标记解析、继承校验、按宿主创建函数选择构造器的目录更新、显式文件变更计划/更新和自举再生，并提供生成代码运行及失败清理回归。首次构建不需要其他仓库、旧 oicc 二进制或联网下载依赖。第一次使用请阅读 [OpenOICC 用户指南](docs/openoicc-user-guide.md)，完整命令、支持语法与一致性边界见 [OpenOICC 生成契约](docs/openoicc.md) 和 [原工具功能核对](docs/oicc-comparison.md)。

## 构建与运行

安装 xmake 和 C11 工具链。Windows 使用完整 MinGW-w64，并将其工具加入 PATH；在仓库根目录运行：

```sh
xmake f -P . -p mingw -m debug
xmake -P . openoicc
xmake run -P . openoicc --help
```

Linux 可将配置命令替换为 `xmake f -P . --toolchain=gcc -m debug`。详细流程与实际验证边界见 [构建说明](docs/build.md)。默认 `xmake -P .` 构建 openoicc 及 NEOioic 静态库；参考程序需要显式选择。

```sh
xmake -P . oioic_reference
xmake run -P . oioic_reference
python tests/test_openoicc.py --openoicc build/mingw/x86_64/debug/openoicc.exe
```

## 项目资料

- [开发指南与架构](AGENTS.md)
- [NEOioic 模型与生成契约](docs/oioic-reference.md)
- [OpenOICC 用户指南](docs/openoicc-user-guide.md)
- [OpenOICC 生成契约与限制](docs/openoicc.md)
- [测试说明](tests/README.md)
- [本地依赖来源](third_party/neoioic/README.md)
- [继承参考示例](examples/oioic_reference/README.md)
- [第三方声明](THIRD_PARTY_NOTICES.md)

源码与必要生成代码纳入 Git，构建缓存和机器设置由忽略规则排除。所有依赖源码随仓库提供，目录引用均相对于仓库，便于其他开发者独立阅读和构建。

## 许可证

项目使用 [MIT License](LICENSE)。NEOioic 运行时与摘选示例保留其原有版权和 MIT 许可，详见 [第三方声明](THIRD_PARTY_NOTICES.md)。
