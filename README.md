# Contest PPT Studio · 竞赛 PPT 设计工坊

[English](README.en.md) · [Skill 入口](SKILL.md) · [验证范围](docs/VALIDATION.md) · [首版说明](docs/RELEASE_NOTES_v0.1.0.md)

**从比赛规则与项目材料出发，先明确内容与视觉方向，再制作尽可能原生可编辑的答辩 PPT。**

面向大创、职业规划、挑战杯等学生竞赛。提供材料诊断、补充提示词、制作需求梳理和图片展板预览，并结合可用的 PPT、生图与渲染工具，组织逐字矢量标题、原生图表、流程图和精细对象动画。

**v0.1.0 · 初始版本。** 这是工作流 skill 与只读检查工具；完整制作需要宿主提供相应能力。已验证的结构与场景，以及尚未完成的真实项目和播放测试，见[验证记录](docs/VALIDATION.md)。

## 工作流程

```mermaid
flowchart LR
    A[读取比赛规则与项目材料] --> B[缺口清单与补充提示词]
    B --> C[图片展板预览]
    C --> D[用户选定风格]
    D --> E[补齐关键材料并确认需求]
    E --> F[原生 PPT 与逐元素动画]
    F --> G[结构、视觉及目标软件检查]
    G --> H[交付可复现项目包]
```

允许先预览、后补齐内容；假设会明确标注。比赛硬性限制与官方模板保护优先。

## 核心设计

| 能力 | 默认做法 |
|---|---|
| 竞赛叙事 | 按实际年份、赛道、阶段与评审要求重构内容；保留事实原意 |
| 材料补充 | 指出缺口、影响与所需证据，给出可复制提示词；不补造成果 |
| 风格未定 | 3 个方向，每方向 1 张包含封面、典型内容页、结尾页的图片展板 |
| 风格已定 | 1 张指定风格三页展板，确认后扩展全套 |
| 官方固定模板 | 保留锁定页和对象；视觉系统已固定时提供 1 张合规填充展板 |
| 主标题 | 逐字设计，优先每字独立的原生矢量轮廓，便于调形状、颜色与排布 |
| 内容与图解 | 正文保留文本框，图表、表格、流程与装饰尽可能原生可编辑 |
| 视觉层次 | 封面搜集 5–10 张候选素材，择优采用抠图、蒙版、柔化及字色匹配光效 |
| 动效 | 对文字、图形和装饰分别安排进入顺序、触发、时长与延迟 |
| 交付 | PPTX、预览、源文件、素材、图表数据、需求、来源记录、动画配置与检查报告 |

转轮廓后的主标题可以改形状与颜色；换字需要从保留的源文字重建。它与直接改字的文本框是不同编辑方式。

## 安装与使用

下载并解压本仓库，将包含 `SKILL.md` 的 `contest-ppt-studio` 文件夹放入宿主实际使用的技能目录，保留 `agents/`、`references/` 和 `scripts/` 的相对结构。

当前 Codex 官方文档列出的本地目录包括用户级 `~/.agents/skills/` 和项目级 `.agents/skills/`。已有自定义或旧版目录时以实际宿主配置为准；不要覆盖已有同名技能。[OpenAI 官方技能说明](https://learn.chatgpt.com/docs/build-skills)

在 Codex 中调用：

```text
使用 $contest-ppt-studio，根据我提供的比赛规则、项目计划书和制作限制，
先检查材料缺口并给出补充提示词，再展示风格展板。
选定风格并确认制作需求后，制作尽可能原生可编辑的答辩 PPT。
```

建议一并提供：比赛名称与赛道、最新项目材料、官方模板、页数与时长限制、参考图。每次制作确认 PowerPoint 或 WPS；缺失的关键项按顺序询问。

其他兼容 Agent 可按其技能发现机制加载 `SKILL.md`，但其工具与问答接口需要适配，跨宿主完整流程尚未验证。

## 依赖与能力边界

- 材料分析与需求策划：需要能读取相应文件的 Agent。
- 图片展板和定制素材：需要可用的图片生成或真实图片渲染能力。
- PPT 制作：需要支持所需原生对象的后端；可按任务评估 [PPT Master](https://github.com/hugohe3/ppt-master) 等现有能力。
- 视觉探索：可结合 [huashu-design](https://github.com/alchaincyf/huashu-design) 等设计工作流。
- 最终验收：需要最终 PPTX 渲染，以及当次指定 PowerPoint/WPS 的编辑和播放检查。
- 随附检查器和自测：仅使用 Python 标准库；本地验证环境为 Python 3.12。

本仓库不包含第三方 PPT 引擎、模型服务、Office 软件或字体，也不会自动安装后端或调用付费服务。第三方项目分别遵守自己的许可，见[依赖与致谢](THIRD_PARTY_NOTICES.md)。

## 可运行的检查工具

在仓库根目录运行：

```bash
python scripts/self_test.py
python scripts/inspect_pptx.py examples/native-smoke/native-smoke.pptx --plan examples/native-smoke/object-plan.json --output qa/native-smoke.json
```

检查器只读盘点对象、资源关系、原生图表/表格、自定义几何、进入动画目标及模板保护哈希。对象断言格式见[交付与检查规范](references/delivery-and-qa.md)。

**结构通过不能代表视觉或播放通过。** 缺少实际软件测试时，报告必须保留“未验证”状态。

## 首版展示与验证

- 21 项检查器测试已在本地通过。
- 4 类桌面场景已评估：未知风格、指定风格、固定官方模板、交付修复；模板分支经过修订回归。
- 提供[三页结构样例](examples/native-smoke/README.md)：4 个独立汉字轮廓、1 个原生图表、1 个原生表格及 12 条进入动画，附生成源与读回记录。
- GitHub Actions 已在 Windows 和 Ubuntu 上通过 Python 3.12 自测与样例结构检查，见[远程检查记录](https://github.com/kukudefu-design/contest-ppt-studio/actions/runs/40315960241)。

样例用于验证结构与工具接口，不是真实竞赛设计成品。真实材料全流程、逐页视觉和 PowerPoint/WPS 实机播放尚未验证。完整边界见 [VALIDATION.md](docs/VALIDATION.md)。

## 项目结构

```text
SKILL.md                  工作流入口
agents/openai.yaml         技能界面与调用设置
references/               材料、视觉、后端与验收规范
scripts/                  只读检查器与自测
examples/native-smoke/    结构样例、生成源与检查记录
docs/                     验证、首版说明与发布指引
```

## 反馈与贡献

反馈时请提供脱敏后的最小材料、期望效果、实际结果、相关工具/软件版本和错误信息。改动后运行 `python scripts/self_test.py`。请保持事实边界、模板保护、可编辑性和验证范围说明。

## 许可证

本项目原创代码与文档采用 [MIT License](LICENSE)。第三方工具、字体及用户素材的授权分别处理。本项目为独立社区项目。
