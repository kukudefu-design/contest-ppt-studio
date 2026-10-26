# Dependencies and acknowledgments

The MIT license in this repository applies to original project code and documentation. Third-party software, services, fonts, and user-provided materials retain their own terms. No third-party presentation engine or font file is bundled here.

## Optional presentation and design backends

- [PPT Master](https://github.com/hugohe3/ppt-master): a candidate native-PPTX workflow and the animation API used for the structural example. Follow the actual installed version's instructions, integrity checks, dependencies, and license. The backend's source code and animation-preset library are not redistributed in this repository.
- [huashu-design](https://github.com/alchaincyf/huashu-design): an optional design and visual-exploration workflow. No source code or assets are copied into this project. Validate its actual export behavior for the current task.
- [python-pptx](https://github.com/scanny/python-pptx) and [fontTools](https://github.com/fonttools/fonttools): optional dependencies for regenerating the synthetic structural example. They are not needed by the inspector or self-tests and are not bundled.

These acknowledgments do not claim endorsement, formal integration certification, or compatibility with all versions.

## Example font

The public structural example uses **Noto Sans SC** to obtain the outlines of the two example characters. Body text requests the same font family; viewers without it may substitute a font. No font file is embedded or distributed with this release.

- Source: [Google Fonts / Noto Sans SC](https://github.com/google/fonts/tree/main/ofl/notosanssc).
- Font download: [NotoSansSC variable TTF](https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf).
- Upstream license: [SIL Open Font License 1.1](https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/OFL.txt).
- Upstream notice: Copyright 2014–2021 Adobe, with Reserved Font Name “Source”.
- Font-file SHA-256 used for the example: `a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da`.

Font software keeps its upstream license. The upstream OFL states that its font-license requirement does not apply to documents created with the font.

## GitHub Actions

The optional CI configuration references [actions/checkout](https://github.com/actions/checkout) and [actions/setup-python](https://github.com/actions/setup-python) at verified v7 commit IDs. Their implementations are not bundled. The workflow checks structural tests only and needs no model-service credentials.

## Host and format documentation

- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills).
- [Agent Skills specification](https://agentskills.io/specification).
- [GitHub: Mermaid diagrams in Markdown](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams).

The project is independently maintained and does not represent these organizations.
