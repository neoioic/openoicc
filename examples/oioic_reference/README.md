# OIOIC 继承参考示例

本目录摘选 OIOIC 1.0.18 多继承示例的 C 源码及头文件，保留原始目录关系和实现。通过根构建链接仓库内 OIOIC 核心，不使用外部仓库。

```text
amphicar
├── car ── vehicle ── OIOIC
└── ship ─ vehicle ── OIOIC
```

vehicle 与 OIOIC 是共享节点，各只构造一次。car 和 ship 的构造器同时提供单继承参考。主程序输出重量、载重及速度，并演示成功路径下的创建、打开、交互、关闭与销毁。

从仓库根目录运行 `xmake -P . oioic_reference` 和 `xmake run -P . oioic_reference`，先按 [构建说明](../../docs/build.md) 配置工具链。

阅读入口：`ho.c` 为宿主；`so/go/car/car.c` 为单继承构造；`so/go/amphicar/amphicar.c` 为菱形构造；`so/ao/Main/Main.c` 为调用示例。Factory 与 Main 的空 `<crt>` 区域是上游保留模板，不代表已有构造器。

示例的业务失败处理有所简化，运行成功只证明这一成功路径，不证明分配失败、部分关闭等路径已覆盖。实现 OpenOICC 时遵循 [生成契约](../../docs/openoicc.md)，不要直接复制简化的错误处理。

来源见 [SOURCE.json](../../third_party/oioic/SOURCE.json)，许可见 [LICENSE](LICENSE)。
