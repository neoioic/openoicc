# 第三方来源与许可

本项目摘选了赵平智设计的 OIOIC 1.0.18，导入基线为提交 `9dad644e8bae1fbdba4ced0965627dda06c3e7e3`。

| 范围 | 来源内容 | 许可 |
| --- | --- | --- |
| `third_party/oioic/` | 公共头文件、核心运行时及静态库构建定义 | [OIOIC MIT](third_party/oioic/LICENSE) |
| `examples/oioic_reference/` | 多继承示例中的宿主、节点、接口及程序入口 | [示例 MIT](examples/oioic_reference/LICENSE) |
| 根 `.clang-format`、`.editorconfig` | OIOIC 代码排版配置 | [OIOIC MIT](third_party/oioic/LICENSE) |
| `docs/oioic-reference.md` 中的 OIOIC 设计说明 | 从 OIOIC 架构、教程、代码风格及工具说明中提炼 | [OIOIC MIT](third_party/oioic/LICENSE) |

原 MIT 版权声明为 `Copyright (c) 2026 赵平智`，源码中的历史作者与版权声明原样保留。根目录项目许可证另见 [LICENSE](LICENSE)。分发上述源码、示例及实质性衍生内容时，附带相应版权和许可声明。

原文件来源路径与导入校验值记录在 [SOURCE.json](third_party/oioic/SOURCE.json)。本项目没有导入上游生成器二进制；OpenOICC 工具已独立实现初版。OIOIC 核心继续作为生产依赖，参考示例继续作为生成代码的行为对照基线；以上材料及其许可、来源记录均仍在使用。
