# 构建与验证

## 依赖与目标

需要 xmake 和支持 C11 的完整 GCC 或 Clang 工具链。OIOIC 源码在仓库内，不需要子模块、另一个工作区、旧生成器或构建时下载。

目标为 `oioic` 静态库、`oicc` 生成器和 `oioic_reference` 控制台参考程序。默认构建库与生成器；参考程序显式选择。命令与生成契约见 [oicc 使用说明](oicc.md)。

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

参考程序成功时输出 car、ship、amphicar 的性能参数，共 11 项。它仅验证摘选运行时与参考示例的正常路径。生成器回归另使用 Python 3 标准库驱动真实命令及 PATH 中的 GCC 编译生成代码：

```sh
xmake -P . oicc
python tests/test_oicc.py --oicc build/mingw/x86_64/debug/oicc.exe
xmake f -P . -p mingw -a x86_64 -m release
xmake -P . oicc
python tests/test_oicc.py --oicc build/mingw/x86_64/release/oicc.exe --release
```

Linux 将可执行路径替换为 `build/linux/x86_64/debug/oicc`（Release 同理）。测试只在仓库 `build/tests/` 内创建和清理自己的独占临时目录，不修改参考示例；测试源码、输入模板和固定随机种子纳入版本管理。`--release` 用 `-O2 -DNDEBUG` 编译测试生成代码，校验本身不依赖 assert。

不同平台的构建命令代表支持目标，不自动代表已验证。当前验证记录见本文件末尾，不能以某一平台成功运行推断其他平台通过。

## 当前记录

2026-10-14：Windows x86_64、MinGW-w64 GCC 15.1.0、xmake 2.9.6 下，仓库内 OIOIC 静态库及 `oioic_reference` 的 Debug/Release 编译链接通过，参考程序两种配置均退出 0，输出 11 项性能参数；默认静态库构建也通过。构建只使用本仓库源码依赖。

源码快照未修改；源文件字节 SHA-256 与来源清单一致，依赖 LICENSE 在还原导入时 CRLF 后匹配（工作区文本换行已规范化）。公开文档和构建定义未包含本机绝对路径或相邻仓库依赖。Linux/macOS 原生构建及 Clang 链接仍未经验证。

2026-10-14：同一 Windows x86_64、MinGW-w64 GCC 15.1.0 环境下，oicc 的 xmake Debug/Release 构建均通过。两种配置分别执行 `tests/test_oicc.py` 的 18 组完整回归，以及新增 Windows 只读文件提交失败/恢复回归，共 19 组均通过；Release 测试生成代码使用 `-O2 -DNDEBUG`。覆盖标记与预处理边界、UTF-8/BOM、单继承/菱形/固定随机多分支图/120 层继承、未知或重复节点及环、区外保留、LF/CRLF、空格路径、重复生成、工具一份有效输入的全部分配点故障、队列分配失败、席位上限、动态/外部存储、OID 回收、部分关闭与打开失败后的重试，以及工具自举再生与重编译。原参考构造器与新生成构造器的 11 项业务输出一致；菱形嵌套委托实测席位峰值为 1、2、3、4、2，调用结束记录清空。未运行旧 oicc 二进制，不宣称其接口或输出完全一致。
