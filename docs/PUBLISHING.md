# GitHub 首版发布指引

本目录包含源码与展示材料，以下步骤适用于首次上传及后续发布。

## 仓库设置

- 名称：`contest-ppt-studio`。
- 可见性：Public。
- README：本包的 `README.md` 为中文首页，`README.en.md` 为英文说明。
- 许可证：MIT；保留仓库所有者的版权署名 `kukudefu-design`。
- 建议 Topics：`agent-skills`、`codex-skill`、`powerpoint`、`pptx`、`presentation`、`student-competition`。

英文 Description：

```text
An agent skill for editable presentations for student competitions, including innovation projects, career planning, and Challenge Cup. Supports material review, requirement clarification, style previews, and tool-assisted creation of vector titles, native charts, and object animations.
```

## 上传源码

1. 解压发布 ZIP，打开其中的 `contest-ppt-studio` 文件夹。
2. 在 GitHub 仓库点击 **Add file → Upload files**。
3. 将该文件夹内的文件和子目录上传，包含 `.github/`、`.gitignore`。仓库根目录应直接出现 `README.md` 和 `SKILL.md`。
4. 若 GitHub 已自动生成 README、LICENSE 或 `.gitignore`，先对照并合并你希望保留的内容，再提交本版文件。
5. 提交说明可用：`Prepare v0.1.0: competition PPT workflow and structural inspector`。

上传方法以 [GitHub 官方说明](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository) 为准。README 的 Mermaid 工作流使用 [GitHub 支持的图表语法](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)。

## 创建 Release

1. 上传完成后检查 README 中英文链接、样例下载、许可证和文件层级。
2. 查看 Actions 是否实际运行；状态未通过时保留原始日志并解决，不预填绿色成功标识。
3. 新建 Release，标签 `v0.1.0`，标题 `v0.1.0 · Contest PPT Studio`。
4. 正文复制 [首版说明](RELEASE_NOTES_v0.1.0.md)，建议勾选 Pre-release。
5. 可以把经校验的发布 ZIP 作为附件。保留“真实竞赛全流程与目标软件播放尚未验证”的说明。

项目仓库：https://github.com/kukudefu-design/contest-ppt-studio 。文档使用相对链接。
