# v0.1.0 · Contest PPT Studio

首次公开版本发布说明草稿。上传时可将本页内容粘贴到 GitHub Release 正文。

## 中文

竞赛 PPT 设计工坊是面向大创、职业规划、挑战杯等学生竞赛的 Agent Skill。它从比赛规则和项目材料出发，组织材料诊断、补充提示词、风格图片展板、制作需求确认、原生 PPT 与精细对象动画，以及可追溯的项目包交付。

### 本版包含

- 明确的“未知风格3张展板 / 指定风格1张展板”流程，每张包含封面、典型内容页和结尾页。
- 事实与计划区分、官方模板保护、逐字矢量标题和原生图表/流程图要求。
- 只读 PPTX 检查器和21项标准库自测。
- 中英双语 README、依赖与致谢、验证记录及三页结构样例。
- GitHub Actions 结构检查配置，远程运行待仓库上传后确认。

### 使用与验证边界

完整制作依赖宿主可用的 PPT、生图、渲染与目标软件能力，第三方引擎不随包分发。已完成本地结构及场景验证；真实竞赛全流程、逐页视觉和 PowerPoint/WPS 实机播放尚未验证。样例数据均为示意。

建议将此首版标记为 **Pre-release**，在完成真实项目验收后再更新验证状态。

## English

Initial public release of an agent skill for editable student-competition presentations. It provides material review, evidence-aware gap prompts, image-board selection, brief confirmation, native-object and animation contracts, and reproducible handoff guidance.

Included: Chinese/English introductions, a read-only PPTX inspector, 21 self-tests, dependency notices, validation scope, a synthetic three-slide example, and a structural CI workflow.

Full production requires suitable host tools and separately available backends. Hosted CI has not run yet. Real-project end-to-end production, rendered visual approval, and live PowerPoint/WPS playback remain unverified. The example is a structural test artifact, not a finished contest deck.
