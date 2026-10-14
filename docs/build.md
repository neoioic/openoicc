# 构建与验证

## 依赖与目标

需要 xmake 和支持 C11 的完整 GCC 或 Clang 工具链。OIOIC 源码在仓库内，不需要子模块、另一个工作区、旧生成器或构建时下载。

目前目标为 `oioic` 静态库和 `oioic_reference` 控制台参考程序。默认只构建静态库；oicc 生成器目标尚未实现。

## Windows

将完整 MinGW-w64 工具链加入 PATH。在仓库根目录执行：

```sh
xmake f -P . -p mingw -a x86_64 -m debug
xmake -P . oioic_reference
xmake run -P . oioic_reference
```

Release 重新配置为 `xmake f -P . -p mingw -a x86_64 -m release`，然后执行相同构建与运行命令。完整工具链包含编译器、链接器和 `ar`；仅有一个 gcc 可执行文件不够。

若自动探测失败，可在自己的本地 xmake 配置中指定工具链安装位置；不要将该位置写进受版本管理的构建定义或公开文档。

## Linux 与 Clang

```sh
xmake f -P . --toolchain=gcc -m debug
xmake -P . oioic_reference
xmake run -P . oioic_reference
```

Clang 将配置中的 `gcc` 换为 `clang`；Release 将 `debug` 换为 `release`。Windows Clang 仍需要匹配的系统头文件和库。macOS 可使用合适的 C11 工具链，但是否可用以实际验证为准。

## 构建产物与验证边界

所有目标输出到仓库的 `build/`，本地配置在 `.xmake/`，二者被 Git 忽略。完整重建使用 `xmake -P . -r oioic_reference`，清理使用 `xmake clean -P .`。

参考程序成功时输出 car、ship、amphicar 的性能参数，共 11 项。它仅验证摘选运行时与参考示例的正常路径，不是新生成器的测试套件。未来生成器测试须验证生成源码的编译、运行、失败处理及再生稳定性。

不同平台的构建命令代表支持目标，不自动代表已验证。当前验证记录见本文件末尾，不能以某一平台成功运行推断其他平台通过。

## 当前记录

2026-10-14：Windows x86_64、MinGW-w64 GCC 15.1.0、xmake 2.9.6 下，仓库内 OIOIC 静态库及 `oioic_reference` 的 Debug/Release 编译链接通过，参考程序两种配置均退出 0，输出 11 项性能参数；默认静态库构建也通过。构建只使用本仓库源码依赖。

导入源码的 SHA-256 与来源清单一致，Markdown 本地链接及编码检查通过，公开文档和构建定义未包含本机绝对路径或相邻仓库依赖。此次未执行 Linux/macOS 原生构建、Clang 链接或错误路径回归，也未实现或测试新生成器。
