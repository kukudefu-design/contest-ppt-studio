# 三页结构样例 / Three-slide structural example

[下载 PPTX](native-smoke.pptx) · [对象计划](object-plan.json) · [生成源](generate_example.py) · [结构记录](../../docs/validation/structure.json)

**本文件是工具检查样例，内容与数据均为示意，不是真实参赛项目。**

文件包含3页：两页展示逐字原生汉字轮廓与同色系光效，一页展示原生图表、表格和可编辑流程节点。4个字符轮廓为2组“演示”，12条进入动画使用实际对象标识编排。

本版公开样例的字形取自开源 Noto Sans SC；字体源与许可见 [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)。字体原文件没有随包分发。正文请求 Noto Sans SC，客户端没有该字体时可能替换；逐字轮廓不依赖客户端重新排字。

已核对文件结构、原生图表数据读回及动画参数。尚未渲染检查视觉，也未在 PowerPoint/WPS 中编辑或放映。打开样例可作为后续客户端测试的起点，不能把该文件称为已验收的视觉作品。

## 检查已提供的文件

在仓库根目录运行：

```bash
python scripts/inspect_pptx.py examples/native-smoke/native-smoke.pptx --plan examples/native-smoke/object-plan.json --output qa/native-smoke.json
```

## 重新生成样例

可选依赖：`python-pptx`、`fonttools`、兼容版本的 PPT Master 动画接口，以及你自行取得的 Noto Sans SC 字体。它们不属于检查器运行依赖。

```bash
python -m pip install python-pptx fonttools
python examples/native-smoke/generate_example.py --backend /path/to/ppt-master --font /path/to/NotoSansSC.ttf --skill . --output generated/native-smoke
```

将两个 `/path/to/` 参数替换为实际位置。脚本先运行后端完整性检查，并保留结构与动画读回结果；不生成风格图片，不运行目标软件测试。它是维护者的演示工具，不会被 skill 自动调用。

## English

This synthetic example exercises native character outlines, a chart, a table, a diagram node, and object-level animation data. It is not a real competition submission or a visually approved presentation. Its title geometry uses Noto Sans SC; the font is not bundled. The example has structural and animation-readback evidence, but no rendered visual or live PowerPoint/WPS approval.
