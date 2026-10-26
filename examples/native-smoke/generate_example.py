"""Build an actual three-slide structural smoke deck, not a competition design.

Uses local fonts for outline geometry without redistributing font files.
Invocation dependencies are passed explicitly and recorded in smoke-result.json.
"""
import argparse
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', required=True, type=Path)
    ap.add_argument('--font', required=True, type=Path)
    ap.add_argument('--deps', type=Path, default=None)
    ap.add_argument('--skill', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    if args.deps is not None:
        sys.path.insert(0, str(args.deps))
    from fontTools.ttLib import TTFont
    from fontTools.pens.basePen import BasePen
    from fontTools.pens.boundsPen import BoundsPen
    from pptx import Presentation
    from pptx.chart.data import CategoryChartData
    from pptx.dml.color import RGBColor
    from pptx.enum.chart import XL_CHART_TYPE
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.oxml.xmlchemy import OxmlElement
    from pptx.oxml import parse_xml
    from pptx.util import Inches, Pt
    subprocess.run([sys.executable, str(args.backend / 'scripts' / 'attribution_guard.py')], check=True)
    sys.path.insert(0, str(args.backend / 'scripts'))
    from pptx_animations import create_sequence_timing_xml, validate_generated_animation_xml, validate_pptx_animation_package

    font = TTFont(args.font, fontNumber=0)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()

    class DrawingMLPen(BasePen):
        def __init__(self, path, bounds):
            super().__init__(glyphs)
            self.path = path
            self.xmin, self.ymin, self.xmax, self.ymax = bounds

        def point(self, command, points):
            node = OxmlElement(command)
            for x, y in points:
                pt = OxmlElement('a:pt')
                pt.set('x', str(round(x - self.xmin)))
                pt.set('y', str(round(self.ymax - y)))
                node.append(pt)
            self.path.append(node)

        def _moveTo(self, p):
            self.point('a:moveTo', [p])

        def _lineTo(self, p):
            self.point('a:lnTo', [p])

        def _curveToOne(self, p1, p2, p3):
            self.point('a:cubicBezTo', [p1, p2, p3])

        def _qCurveToOne(self, p1, p2):
            self.point('a:quadBezTo', [p1, p2])

        def _closePath(self):
            self.path.append(OxmlElement('a:close'))

        def _endPath(self):
            pass

    def text(slide, value, x, y, w=10, h=.7, size=26):
        shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        shape.text = value
        for paragraph in shape.text_frame.paragraphs:
            paragraph.font.size = Pt(size)
            paragraph.font.name = 'Noto Sans SC'
        return shape

    def glyph(slide, char, x):
        name = cmap[ord(char)]
        pen = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        bounds = pen.bounds
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.1), Inches(1.55), Inches(1.65))
        shape.name = 'glyph-' + char
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string('168A64')
        shape.line.fill.background()
        sppr = shape._element.spPr
        for existing in list(sppr):
            if existing.tag.endswith('}prstGeom'):
                sppr.remove(existing)
        geom = OxmlElement('a:custGeom')
        for key in ('a:avLst', 'a:gdLst', 'a:ahLst', 'a:cxnLst'):
            geom.append(OxmlElement(key))
        paths = OxmlElement('a:pathLst')
        path = OxmlElement('a:path')
        path.set('w', str(round(bounds[2] - bounds[0])))
        path.set('h', str(round(bounds[3] - bounds[1])))
        glyphs[name].draw(DrawingMLPen(path, bounds))
        paths.append(path)
        geom.append(paths)
        sppr.append(geom)
        effects = OxmlElement('a:effectLst')
        glow = OxmlElement('a:glow')
        glow.set('rad', '36000')
        color = OxmlElement('a:srgbClr')
        color.set('val', '61B99C')
        glow.append(color)
        effects.append(glow)
        sppr.append(effects)
        return shape

    presentation = Presentation()
    presentation.slide_width = Inches(13.333333)
    presentation.slide_height = Inches(7.5)
    plans, expected_motion = [], []
    for number in (1, 2, 3):
        page = presentation.slides.add_slide(presentation.slide_layouts[6])
        title = text(page, f'原生对象与动画检查样例 · {number}', .6, .25)
        text(page, '工具验证文件；示意数据，不代表参赛项目或实测成果。', .6, 6.7, size=17)
        entry = {'index': number, 'required_text_shape_ids': [str(title.shape_id)]}
        targets = [(title.shape_id, 0, 'entrance_fade', .3)]
        if number in (1, 3):
            first, second = glyph(page, '演', 1), glyph(page, '示', 2.9)
            label = text(page, '每字独立原生轮廓 / 同色系光效', 1, 3.2, size=24)
            entry['required_vector_shape_ids'] = [str(first.shape_id), str(second.shape_id)]
            entry['required_glow_shape_ids'] = entry['required_vector_shape_ids']
            targets += [(first.shape_id, 70, 'entrance_fade', .3), (second.shape_id, 70, 'entrance_fade', .3), (label.shape_id, 50, 'entrance_fade', .3)]
        else:
            data = CategoryChartData()
            data.categories = ['演示A', '演示B', '演示C']
            data.add_series('示意数据', (10, 20, 15))
            chart = page.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(.7), Inches(1.4), Inches(6), Inches(4), data)
            table = page.shapes.add_table(2, 2, Inches(7), Inches(1.5), Inches(5), Inches(1.6))
            for row, values in zip(table.table.rows, [('对象', '状态'), ('数据', '示意')]):
                for cell, value in zip(row.cells, values):
                    cell.text = value
            node = page.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.4), Inches(3.8), Inches(3), Inches(.8))
            node.text = '可编辑流程节点'
            entry.update(min_native_charts=1, min_native_tables=1)
            targets += [(chart.shape_id, 80, 'entrance_wipe', .35), (table.shape_id, 80, 'entrance_fade', .3), (node.shape_id, 80, 'entrance_fly', .3)]
        entry['required_entrance_shape_ids'] = [str(row[0]) for row in targets]
        timing = create_sequence_timing_xml(targets, duration=.3, trigger='after-previous')
        wrapper = parse_xml('<root xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">' + timing + '</root>')
        page._element.append(wrapper[0])
        plans.append(entry)
        expected_motion.append(targets)
    args.output.mkdir(parents=True, exist_ok=True)
    deck = args.output / 'native-smoke.pptx'
    presentation.core_properties.author = 'contest-ppt-studio contributors'
    presentation.core_properties.last_modified_by = 'contest-ppt-studio contributors'
    presentation.core_properties.title = 'Structural test example; not a competition submission'
    presentation.save(deck)
    plan = {'slides': plans}
    (args.output / 'object-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    validate_pptx_animation_package(deck, require_supported_effects=True)
    with zipfile.ZipFile(deck) as z:
        motion = [asdict(validate_generated_animation_xml(z.read(f'ppt/slides/slide{i}.xml'), targets, duration=.3, trigger='after-previous')) for i, targets in enumerate(expected_motion, 1)]
    spec = importlib.util.spec_from_file_location('inspector', args.skill / 'scripts' / 'inspect_pptx.py')
    inspector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inspector)
    report = inspector.inspect_deck(deck, plan)
    assert report['structural_status'] == 'pass', report['issues']
    assert report['plan_coverage'] == 'all_slides'
    (args.output / 'structure.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    check = Presentation(deck)
    assert len(check.slides) == 3
    chart = next(shape.chart for shape in check.slides[1].shapes if shape.has_chart)
    assert list(chart.series[0].values) == [10.0, 20.0, 15.0]
    result = {'slide_count': 3, 'native_glyph_count': sum(len(p.get('required_vector_shape_ids', [])) for p in plans), 'chart_data_roundtrip': 'pass', 'animation_package_and_exact_readback': 'pass', 'motion_rows': motion, 'visual_validation': 'not_run', 'playback_validation': 'not_run', 'font_source': str(args.font), 'backend': str(args.backend)}
    (args.output / 'smoke-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'motion_rows'}, ensure_ascii=False))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
