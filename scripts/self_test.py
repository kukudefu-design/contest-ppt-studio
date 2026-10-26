"""Structural fixtures only; these ZIPs are not slideshow/render fixtures."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import unittest
import zipfile

_HERE = Path(__file__).resolve()
_DEFAULT = _HERE.parents[1] if (_HERE.parent / 'inspect_pptx.py').is_file() else _HERE.parents[1] / 'contest-ppt-studio'
SKILL_DIR = Path(os.environ.get("CONTEST_SKILL_DIR", str(_DEFAULT)))
SCRIPT = SKILL_DIR / "scripts" / "inspect_pptx.py"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def rels(rows):
    return f'<Relationships xmlns="{PKG}">' + "".join(f'<Relationship Id="{key}" Type="{R}/{kind}" Target="{target}"/>' for key, kind, target in rows) + '</Relationships>'


def slide_xml(text, target="2", category="entr", raster_only=False):
    opening = f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}" xmlns:c="{C}"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name="root-group"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
    if raster_only:
        objects = '<p:pic><p:nvPicPr><p:cNvPr id="4" name="page-image"/></p:nvPicPr><p:blipFill><a:blip r:embed="rImage"/></p:blipFill></p:pic>'
    else:
        objects = f'''<p:sp><p:nvSpPr><p:cNvPr id="2" name="body"/></p:nvSpPr><p:spPr><a:prstGeom prst="rect"/></p:spPr><p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="3" name="glyph-1"/></p:nvSpPr><p:spPr><a:custGeom><a:pathLst><a:path w="100" h="100"><a:moveTo><a:pt x="0" y="0"/></a:moveTo><a:lnTo><a:pt x="100" y="100"/></a:lnTo><a:close/></a:path></a:pathLst></a:custGeom><a:effectLst><a:glow rad="20000"><a:srgbClr val="44AA88"/></a:glow></a:effectLst></p:spPr></p:sp>
<p:pic><p:nvPicPr><p:cNvPr id="4" name="photo"/></p:nvPicPr><p:blipFill><a:blip r:embed="rImage"/></p:blipFill></p:pic>
<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="5" name="table"/></p:nvGraphicFramePr><a:graphic><a:graphicData><a:tbl><a:tr><a:tc><a:txBody><a:p><a:r><a:t>cell</a:t></a:r></a:p></a:txBody></a:tc></a:tr></a:tbl></a:graphicData></a:graphic></p:graphicFrame>
<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="6" name="chart"/></p:nvGraphicFramePr><a:graphic><a:graphicData><c:chart r:id="rChart"/></a:graphicData></a:graphic></p:graphicFrame>'''
    timing = f'<p:timing><p:tnLst><p:par><p:cTn id="1" presetClass="{category}"><p:childTnLst><p:animEffect transition="in"><p:cBhvr><p:cTn id="2"/><p:tgtEl><p:spTgt spid="{target}"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>' if target else ''
    return opening + objects + '</p:spTree></p:cSld>' + timing + '</p:sld>'


def make_fixture(path, order=(1, 2), broken_resource=False, target="2", category="entr", raster_only=False):
    parts = {
        '[Content_Types].xml': '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        'ppt/presentation.xml': f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst>' + ''.join(f'<p:sldId id="{255+i}" r:id="rSlide{i}"/>' for i in order) + '</p:sldIdLst><p:sldSz cx="12192000" cy="6858000"/></p:presentation>',
        'ppt/_rels/presentation.xml.rels': rels([(f'rSlide{i}', 'slide', f'slides/slide{i}.xml') for i in (1, 2)]),
        'ppt/charts/chart1.xml': f'<c:chartSpace xmlns:c="{C}"><c:chart/></c:chartSpace>',
        'ppt/media/image1.png': b'fixture-resource-not-rendered',
    }
    for i in (1, 2):
        parts[f'ppt/slides/slide{i}.xml'] = slide_xml(f'page-{i}', target, category, raster_only)
        parts[f'ppt/slides/_rels/slide{i}.xml.rels'] = rels([
            ('rImage', 'image', '../media/missing.png' if broken_resource else '../media/image1.png'),
            ('rChart', 'chart', '../charts/chart1.xml'),
        ])
    with zipfile.ZipFile(path, 'w') as z:
        for name, value in parts.items():
            z.writestr(name, value)
    return parts


class InspectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('contest_ppt_inspector', SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.deck = Path(self.tmp.name) / 'deck.pptx'

    def codes(self, report):
        return {item['code'] for item in report['issues']}

    def test_actual_presentation_order(self):
        make_fixture(self.deck, order=(2, 1))
        result = self.module.inspect_deck(self.deck)
        self.assertEqual([x['part'] for x in result['slides']], ['ppt/slides/slide2.xml', 'ppt/slides/slide1.xml'])

    def test_native_object_inventory(self):
        make_fixture(self.deck)
        result = self.module.inspect_deck(self.deck)
        page = result['slides'][0]
        self.assertEqual(page['text_shape_ids'], ['2'])
        self.assertEqual(page['custom_geometry_shape_ids'], ['3'])
        self.assertEqual(page['native_chart_count'], 1)
        self.assertEqual(page['native_table_count'], 1)
        self.assertEqual(page['picture_count'], 1)
        self.assertEqual(page['glow_shape_ids'], ['3'])
        self.assertEqual(result['structural_status'], 'pass')

    def test_missing_relationship_resource_fails(self):
        make_fixture(self.deck, broken_resource=True)
        result = self.module.inspect_deck(self.deck)
        self.assertEqual(result['structural_status'], 'fail')
        self.assertIn('missing_relationship_target', self.codes(result))

    def test_missing_animation_target_fails(self):
        make_fixture(self.deck, target='999')
        result = self.module.inspect_deck(self.deck)
        self.assertIn('missing_animation_target', self.codes(result))

    def test_inventory_cannot_claim_playback_or_visual_success(self):
        make_fixture(self.deck)
        result = self.module.inspect_deck(self.deck)
        self.assertFalse(result['plan_checked'])
        self.assertEqual(result['visual_validation'], 'not_run')
        self.assertEqual(result['playback_validation'], 'not_run')

    def test_picture_does_not_satisfy_glyph_requirement(self):
        make_fixture(self.deck)
        plan = {'slides': [{'index': 1, 'required_vector_shape_ids': ['4']}]}
        result = self.module.inspect_deck(self.deck, plan)
        self.assertIn('required_vector_missing', self.codes(result))

    def test_emphasis_does_not_satisfy_entrance_requirement(self):
        make_fixture(self.deck, category='emph')
        plan = {'slides': [{'index': 1, 'required_entrance_shape_ids': ['2']}]}
        result = self.module.inspect_deck(self.deck, plan)
        self.assertIn('required_entrance_missing', self.codes(result))

    def test_plan_matches_real_objects(self):
        make_fixture(self.deck)
        plan = {'slides': [{'index': 1, 'required_text_shape_ids': ['2'], 'required_vector_shape_ids': ['3'], 'required_glow_shape_ids': ['3'], 'required_entrance_shape_ids': ['2'], 'min_native_charts': 1, 'min_native_tables': 1}]}
        result = self.module.inspect_deck(self.deck, plan)
        self.assertTrue(result['plan_checked'])
        self.assertEqual(result['plan_status'], 'pass')

    def test_protected_part_hash_detects_change(self):
        make_fixture(self.deck)
        result = self.module.inspect_deck(self.deck, {'protected_parts': {'ppt/slides/slide1.xml': hashlib.sha256(b'original').hexdigest()}})
        self.assertIn('protected_part_changed', self.codes(result))

    def test_invalid_plan_is_not_silently_accepted(self):
        make_fixture(self.deck)
        result = self.module.inspect_deck(self.deck, {'slides': [{'index': 20}, {'index': 1, 'min_native_charts': -1}]})
        self.assertEqual(result['plan_status'], 'fail')
        self.assertIn('invalid_plan', self.codes(result))

    def test_raster_only_warning(self):
        make_fixture(self.deck, raster_only=True, target=None)
        result = self.module.inspect_deck(self.deck)
        self.assertIn('raster_only_slide', self.codes(result))

    def test_empty_geometry_is_not_a_glyph_outline(self):
        parts = make_fixture(self.deck)
        parts['ppt/slides/slide1.xml'] = parts['ppt/slides/slide1.xml'].replace('<a:pathLst><a:path w="100" h="100"><a:moveTo><a:pt x="0" y="0"/></a:moveTo><a:lnTo><a:pt x="100" y="100"/></a:lnTo><a:close/></a:path></a:pathLst>', '')
        with zipfile.ZipFile(self.deck, 'w') as z:
            for name, value in parts.items():
                z.writestr(name, value)
        result = self.module.inspect_deck(self.deck, {'slides': [{'index': 1, 'required_vector_shape_ids': ['3']}]})
        self.assertIn('required_vector_missing', self.codes(result))

    def test_partial_plan_exposes_unchecked_slides(self):
        make_fixture(self.deck)
        result = self.module.inspect_deck(self.deck, {'slides': [{'index': 1, 'required_text_shape_ids': ['2']}]})
        self.assertEqual(result['plan_coverage'], 'partial')
        self.assertEqual(result['unplanned_slide_indices'], [2])

    def test_null_cli_plan_cannot_bypass_checks(self):
        make_fixture(self.deck)
        plan = Path(self.tmp.name) / 'plan.json'
        plan.write_text('null', encoding='utf-8')
        proc = subprocess.run([sys.executable, str(SCRIPT), str(self.deck), '--plan', str(plan)], capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)

    def test_missing_slide_does_not_shift_plan_indices(self):
        parts = make_fixture(self.deck)
        parts['ppt/slides/slide1.xml'] = 'invalid XML'
        with zipfile.ZipFile(self.deck, 'w') as z:
            for name, value in parts.items():
                z.writestr(name, value)
        result = self.module.inspect_deck(self.deck, {'slides': [{'index': 2, 'required_vector_shape_ids': ['3']}]})
        self.assertNotIn('invalid_plan', self.codes(result))
        self.assertEqual(result['slides'][0]['index'], 2)

    def test_nested_emphasis_cannot_inherit_entrance_class(self):
        parts = make_fixture(self.deck)
        extra = '<p:par><p:cTn id="3" presetClass="emph"><p:childTnLst><p:animEffect transition="none"><p:cBhvr><p:cTn id="4"/><p:tgtEl><p:spTgt spid="6"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>'
        parts['ppt/slides/slide1.xml'] = parts['ppt/slides/slide1.xml'].replace('</p:animEffect></p:childTnLst>', '</p:animEffect>' + extra + '</p:childTnLst>', 1)
        with zipfile.ZipFile(self.deck, 'w') as z:
            for name, value in parts.items():
                z.writestr(name, value)
        result = self.module.inspect_deck(self.deck, {'slides': [{'index': 1, 'required_entrance_shape_ids': ['6']}]})
        self.assertIn('required_entrance_missing', self.codes(result))

    def test_root_group_id_collisions_are_detected(self):
        parts = make_fixture(self.deck)
        parts['ppt/slides/slide1.xml'] = parts['ppt/slides/slide1.xml'].replace('id="1" name="root-group"', 'id="2" name="root-group"')
        with zipfile.ZipFile(self.deck, 'w') as z:
            for name, value in parts.items():
                z.writestr(name, value)
        self.assertIn('duplicate_shape_id', self.codes(self.module.inspect_deck(self.deck)))

    def test_corrupt_deflate_returns_failure_json(self):
        parts = make_fixture(self.deck)
        with zipfile.ZipFile(self.deck, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for name, value in parts.items():
                z.writestr(name, value)
        with zipfile.ZipFile(self.deck) as z:
            offset = z.getinfo('ppt/presentation.xml').header_offset
        data = bytearray(self.deck.read_bytes())
        name_length, extra_length = struct.unpack_from('<HH', data, offset + 26)
        data[offset + 30 + name_length + extra_length] = 255
        self.deck.write_bytes(data)
        result = self.module.inspect_deck(self.deck)
        self.assertEqual(result['structural_status'], 'fail')
        proc = subprocess.run([sys.executable, str(SCRIPT), str(self.deck)], capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)['structural_status'], 'fail')

    def test_empty_page_assertions_cannot_pass(self):
        make_fixture(self.deck)
        result = self.module.inspect_deck(self.deck, {'slides': [{'index': 1, 'min_native_charts': 0}]})
        self.assertEqual(result['plan_status'], 'fail')

    def test_plan_without_any_assertions_cannot_pass(self):
        make_fixture(self.deck)
        result = self.module.inspect_deck(self.deck, {'slides': [], 'protected_parts': {}})
        self.assertEqual(result['plan_status'], 'fail')

    def test_invalid_zip_cli_has_json_error_and_nonzero_exit(self):
        self.deck.write_text('not a pptx', encoding='utf-8')
        proc = subprocess.run([sys.executable, str(SCRIPT), str(self.deck)], capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)
        result = json.loads(proc.stdout)
        self.assertEqual(result['structural_status'], 'fail')
        self.assertIn('invalid_package', self.codes(result))


if __name__ == '__main__':
    unittest.main(verbosity=2)
