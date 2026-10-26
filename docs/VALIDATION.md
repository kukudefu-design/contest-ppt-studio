# v0.1.0 验证范围 / Validation scope

准备日期：2026-10-26。验证对象为本仓库的 skill、只读检查器和教学结构样例。

## 已有证据

| 范围 | 已执行的检查 | 不能据此推断 |
|---|---|---|
| Skill 文件 | 官方入口结构校验；引用与界面配置检查 | 所有宿主、模型和工具组合均已兼容 |
| Python 检查器 | 21 项标准库自测，本次发布副本重新执行 | 完整 Office XSD、视觉或播放已通过 |
| 场景决策 | 未知风格、指定风格、固定模板、交付修复共4类桌面推演；模板分支修订后回归 | 这些案例已实际生成展板或整套 PPT |
| 公开结构样例 | 3页、4个独立汉字轮廓、1个原生图表、1个原生表格、12条进入动画 | 真实竞赛设计质量或现场答辩效果 |
| 图表 | 原生图表的示意数据重新读取为10、20、15 | 这是项目实测、行业数据或竞赛成果 |
| 动画 | PPT Master 接口执行包结构校验及目标、顺序、效果、触发、时长读回核对 | PowerPoint/WPS 中实际放映一致 |
| 公开包 | 原始8个技能文件与已安装版本逐文件一致；路径和打包内容检查 | 没有任何潜在缺陷或适用于所有系统 |

## 可重复运行

```bash
python -B -X utf8 scripts/self_test.py
python -B -X utf8 scripts/inspect_pptx.py examples/native-smoke/native-smoke.pptx --plan examples/native-smoke/object-plan.json --output qa/native-smoke.json
```

本地测试输出见 [inspector-tests.txt](validation/inspector-tests.txt)，样例结构输出见 [structure.json](validation/structure.json)，动画读回摘要见 [motion-readback.json](validation/motion-readback.json)。发布记录移除了本机安装目录、字体本地路径和用户会话内容。

GitHub Actions 配置将以 Python 3.12 在 Windows 和 Ubuntu 运行同类检查。**远程工作流尚未执行**，不能用本地成功代替 CI 成功或 Linux 兼容结论。

## 尚未执行

- 真实比赛材料从诊断、图片展板到全套 PPT 交付的完整运行。
- 本次公开样例从最终 PPTX 渲染后的逐页人工视觉验收。
- PowerPoint/WPS 中的实际对象编辑、动画放映和讲述节奏测试。
- 干净机器的完整制作环境重建及所有第三方后端版本兼容测试。

因此，本版定位为初始工作流与检查工具发布。结构样例用于展示对象与动画的文件结构，不作为已经验收的竞赛视觉作品。

## English summary

Twenty-one inspector self-tests passed locally. Four tabletop cases assessed workflow decisions; the fixed-template case was clarified and retested. The three-slide synthetic example contains four independent outlined characters, a native chart and table, and twelve entrance-animation rows, with structural and parameter readback checks.

Hosted CI, real-project end-to-end generation, rendered visual QA, live PowerPoint/WPS editing/playback, and clean-machine production reproduction remain unverified. Structural inventory and animation XML do not establish visual or playback success.
