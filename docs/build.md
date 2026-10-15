# 构建与验证

## 依赖与目标

需要 xmake 和支持 C11 的完整 GCC 或 Clang 工具链。OIOIC 源码在仓库内，不需要子模块、另一个工作区、旧生成器或构建时下载。

目标为 `oioic` 静态库、`openoicc` 生成器和 `oioic_reference` 控制台参考程序。默认构建库与生成器；参考程序显式选择。首次使用见 [OpenOICC 用户指南](openoicc-user-guide.md)，完整规则见 [命令与生成契约](openoicc.md)。Python 3 仅用于回归测试。

## Windows

将完整 MinGW-w64 工具链加入 PATH。在仓库根目录执行：

```sh
xmake f -P . -p mingw -a x86_64 -m debug
xmake -P . openoicc
xmake run -P . openoicc --help
```

Release 重新配置为 `xmake f -P . -p mingw -a x86_64 -m release`，然后执行相同构建与运行命令。完整工具链包含编译器、链接器和 `ar`；仅有一个 gcc 可执行文件不够。

若自动探测失败，可在自己的本地 xmake 配置中指定工具链安装位置；不要将该位置写进受版本管理的构建定义或公开文档。

## Linux 与 Clang

```sh
xmake f -P . --toolchain=gcc -m debug
xmake -P . openoicc
xmake run -P . openoicc --help
```

Clang 将配置中的 `gcc` 换为 `clang`；Release 将 `debug` 换为 `release`。Windows Clang 仍需要匹配的系统头文件和库。macOS 可使用合适的 C11 工具链，但是否可用以实际验证为准。

## 构建产物与验证边界

所有目标输出到仓库的 `build/`，本地配置在 `.xmake/`，二者被 Git 忽略。完整重建工具使用 `xmake -P . -r openoicc`，清理使用 `xmake clean -P .`。另行验证参考程序时执行 `xmake -P . oioic_reference` 和 `xmake run -P . oioic_reference`。

参考程序成功时输出 car、ship、amphicar 的性能参数，共 11 项。它仅验证摘选运行时与参考示例的正常路径。生成器回归另使用 Python 3 标准库驱动真实命令及 PATH 中的 GCC 编译生成代码：

```sh
xmake -P . openoicc
python tests/test_openoicc.py --openoicc build/mingw/x86_64/debug/openoicc.exe
xmake f -P . -p mingw -a x86_64 -m release
xmake -P . openoicc
python tests/test_openoicc.py --openoicc build/mingw/x86_64/release/openoicc.exe --release
```

Linux 将可执行路径替换为 `build/linux/x86_64/debug/openoicc`（Release 同理）。测试只在仓库 `build/tests/` 内创建和清理自己的独占临时目录，不修改参考示例；测试源码、输入模板和固定随机种子纳入版本管理。`--release` 用 `-O2 -DNDEBUG` 编译测试生成代码，校验本身不依赖 assert。

不同平台的构建命令代表支持目标，不自动代表已验证。当前验证记录见本文件末尾，不能以某一平台成功运行推断其他平台通过。

## 当前记录

2026-10-14：Windows x86_64、MinGW-w64 GCC 15.1.0、xmake 2.9.6 下，仓库内 OIOIC 静态库及 `oioic_reference` 的 Debug/Release 编译链接通过，参考程序两种配置均退出 0，输出 11 项性能参数；默认静态库构建也通过。构建只使用本仓库源码依赖。

源码快照未修改；源文件字节 SHA-256 与来源清单一致，依赖 LICENSE 在还原导入时 CRLF 后匹配（工作区文本换行已规范化）。公开文档和构建定义未包含本机绝对路径或相邻仓库依赖。Linux/macOS 原生构建及 Clang 链接仍未经验证。

2026-10-15：Windows x86_64、MinGW-w64 GCC 下，重新构建 Debug/Release，分别执行上述完整测试命令，均为 36 个测试方法全部通过（Debug 约 57 秒、Release 约 74 秒）。新增边界矩阵、随机图运行及故障注入范围见 [测试说明](../tests/README.md)。本轮修复构造区作用域、宏伪绑定与错误返回类型、根名称大小写冲突、孤立 CR、NULL 构造布局及非法对齐值检查。全部仓库文本检查为 LF，`git diff --check` 通过。第三方材料核查后均仍用于构建、行为对照、来源或许可记录，未移除任何第三方材料；测试未修改仓库外文件或系统配置。仍未执行 Linux 或 Clang 验证。

同日更名与文档核对：正式名称统一为 OpenOICC，构建目标、命令、公共头文件目录及测试入口统一为 `openoicc`；输入 `<oicc>` 标记不变。更名后 Windows MinGW Debug/Release 各 36 个测试全部通过（约 53 秒、80 秒）。随后仅调整版本显示和生成代码署名为正式大小写，两种配置重新构建，并分别复测命令行与自举再生通过。用户指南的最小示例从文档提取后实际生成、编译及运行成功，输出 `boat lifecycle passed`；GCC 对原运行时给出已有的未使用参数警告。本地 Markdown 链接、LF 和差异空白检查通过。
