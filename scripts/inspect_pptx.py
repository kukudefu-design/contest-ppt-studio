#!/usr/bin/env python3
"""Read-only PPTX inventory and explicit object-plan checks (Python 3 stdlib).

This is not an Office schema validator, renderer, or slideshow test.
Usage: python inspect_pptx.py deck.pptx [--plan object-plan.json] [--output report.json]
Exit 0: requested structural checks passed; 1: check failures; 2: input/CLI error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile
import zlib

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'asvg': 'http://schemas.microsoft.com/office/drawing/2016/SVG/main',
}
REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
MAX_XML_BYTES = 16 * 1024 * 1024


def _issue(report, code, message, severity='error', slide=None):
    row = {'code': code, 'severity': severity, 'message': message}
    if slide is not None:
        row['slide'] = slide
    report['issues'].append(row)


def _target(source, target):
    value = unquote(target.split('#', 1)[0]).replace('\\', '/')
    result = posixpath.normpath(value.lstrip('/') if value.startswith('/') else posixpath.join(posixpath.dirname(source), value))
    if result == '..' or result.startswith('../'):
        raise ValueError('relationship escapes package root')
    return source if not value else result


def _source_part(rel_name):
    if rel_name == '_rels/.rels':
        return ''
    return posixpath.join(posixpath.dirname(posixpath.dirname(rel_name)), posixpath.basename(rel_name)[:-5])


def _xml(z, name, report):
    try:
        if z.getinfo(name).file_size > MAX_XML_BYTES:
            raise ValueError(f'XML part exceeds {MAX_XML_BYTES} bytes')
        return ET.fromstring(z.read(name))
    except (KeyError, ValueError, ET.ParseError, RuntimeError, zlib.error) as exc:
        _issue(report, 'invalid_xml_part', f'{name}: {exc}')
        return None


def _relationships(z, names, report):
    by_source = {}
    external = 0
    for name in sorted(n for n in names if n.endswith('.rels')):
        root = _xml(z, name, report)
        if root is None:
            continue
        if root.tag != f'{{{REL_NS}}}Relationships':
            _issue(report, 'unsupported_relationship_namespace', name)
            continue
        source = _source_part(name)
        mapping = {}
        for rel in root:
            key = rel.get('Id')
            if not key or key in mapping:
                _issue(report, 'duplicate_relationship_id', f'{name}: {key}')
                continue
            target = rel.get('Target', '')
            row = {'type': rel.get('Type', ''), 'external': rel.get('TargetMode') == 'External'}
            if row['external']:
                external += 1
                row['target'] = target
            else:
                try:
                    row['target'] = _target(source, target)
                    if not target or row['target'] not in names:
                        _issue(report, 'missing_relationship_target', f'{name}: {key} -> {target}')
                except ValueError as exc:
                    row['target'] = ''
                    _issue(report, 'invalid_relationship_target', f'{name}: {exc}')
            mapping[key] = row
        by_source[source] = mapping
    report['external_relationship_count'] = external
    return by_source


def _object_id(node):
    nv = node.find('.//p:cNvPr', NS)
    return nv.get('id') if nv is not None else None


def _slide_inventory(root, part, index, relations, report):
    objects = [node for node in root.iter() if node.tag in {f"{{{NS['p']}}}{tag}" for tag in ('sp', 'cxnSp', 'pic', 'graphicFrame', 'grpSp')}]
    ids = [key for node in objects if (key := _object_id(node)) is not None]
    all_nv_ids = [node.get('id') for node in root.findall('.//p:cNvPr', NS) if node.get('id')]
    if len(all_nv_ids) != len(set(all_nv_ids)):
        _issue(report, 'duplicate_shape_id', part, slide=index)
    text_ids, vector_ids, glow_ids = [], [], []
    charts = tables = pictures = svg_pictures = 0
    for node in objects:
        key = _object_id(node)
        if node.tag == f"{{{NS['p']}}}sp":
            text = ''.join(item.text or '' for item in node.findall('./p:txBody//a:t', NS))
            if text.strip():
                text_ids.append(key)
            if node.find('./p:spPr/a:custGeom/a:pathLst/a:path/*', NS) is not None:
                vector_ids.append(key)
        if node.find('./p:spPr/a:effectLst/a:glow', NS) is not None or node.find('./p:grpSpPr/a:effectLst/a:glow', NS) is not None:
            glow_ids.append(key)
        if node.tag == f"{{{NS['p']}}}pic":
            pictures += 1
            if node.find('.//asvg:svgBlip', NS) is not None:
                svg_pictures += 1
        charts += len(node.findall('./a:graphic/a:graphicData/c:chart', NS))
        tables += len(node.findall('./a:graphic/a:graphicData/a:tbl', NS))
    # Relationship files can be well-formed while the slide references an unknown r:id.
    for node in root.iter():
        for attr in ('id', 'embed', 'link'):
            value = node.get(f"{{{NS['r']}}}{attr}")
            if value and value not in relations:
                _issue(report, 'missing_relationship_id', f'{part}: {value}', slide=index)
    timing = root.find('./p:timing', NS)
    all_targets, entrance_targets = set(), set()
    if timing is not None:
        all_targets = {node.get('spid') for node in timing.findall('.//p:spTgt', NS) if node.get('spid')}
        def classify(node, category=None):
            if node.tag == f"{{{NS['p']}}}cTn" and node.get('presetClass'):
                category = node.get('presetClass')
            if node.tag == f"{{{NS['p']}}}spTgt" and category == 'entr' and node.get('spid'):
                entrance_targets.add(node.get('spid'))
            for child in node:
                classify(child, category)
        classify(timing)
        for target in sorted(all_targets - set(ids)):
            _issue(report, 'missing_animation_target', f'{part}: shape {target}', slide=index)
    if pictures and not text_ids and not charts and not tables and not vector_ids:
        _issue(report, 'raster_only_slide', '图片为主要内容；需要人工核实编辑要求。', 'warning', index)
    return {
        'index': index, 'part': part, 'hidden': root.get('show') == '0',
        'shape_ids': ids, 'object_count': len(objects),
        'text_shape_ids': text_ids, 'custom_geometry_shape_ids': vector_ids,
        'glow_shape_ids': glow_ids, 'native_chart_count': charts,
        'native_table_count': tables, 'picture_count': pictures,
        'svg_picture_count': svg_pictures,
        'animation_target_ids': sorted(all_targets),
        'entrance_target_ids': sorted(entrance_targets),
    }


def _check_plan(z, report, plan):
    def invalid(message):
        _issue(report, 'invalid_plan', message)
    if not isinstance(plan, dict) or not plan:
        invalid('Plan must be a nonempty object.')
        return
    if set(plan) - {'slides', 'protected_parts'}:
        invalid('Unknown top-level plan keys: ' + ', '.join(sorted(set(plan) - {'slides', 'protected_parts'})))
    checks = {
        'required_text_shape_ids': ('text_shape_ids', 'required_text_missing'),
        'required_vector_shape_ids': ('custom_geometry_shape_ids', 'required_vector_missing'),
        'required_glow_shape_ids': ('glow_shape_ids', 'required_glow_missing'),
        'required_entrance_shape_ids': ('entrance_target_ids', 'required_entrance_missing'),
    }
    minimums = {'min_native_charts': 'native_chart_count', 'min_native_tables': 'native_table_count'}
    pages = plan.get('slides', [])
    if not isinstance(pages, list):
        invalid('slides must be an array.')
        pages = []
    if not pages and not plan.get('protected_parts'):
        invalid('Plan contains no object or protected-part assertions.')
    seen = set()
    by_index = {page['index']: page for page in report['slides']}
    for expected in pages:
        if not isinstance(expected, dict):
            invalid('Every slide plan must be an object.')
            continue
        index = expected.get('index')
        if type(index) is not int or index not in by_index or index in seen:
            invalid(f'Invalid or duplicate slide index: {index!r}')
            continue
        seen.add(index)
        page = by_index[index]
        if not any(expected.get(key) for key in checks) and not any(type(expected.get(key)) is int and expected[key] > 0 for key in minimums):
            invalid(f'Slide {index} has no substantive object assertions.')
        if set(expected) - ({'index', 'role'} | set(checks) | set(minimums)):
            invalid(f'Unknown keys on slide {index}.')
        for field, (inventory, code) in checks.items():
            if field not in expected:
                continue
            values = expected[field]
            if not isinstance(values, list) or any(not isinstance(v, str) or not v.isdecimal() for v in values):
                invalid(f'{field} on slide {index} must be an array of numeric ID strings.')
                continue
            missing = set(values) - set(page[inventory])
            if missing:
                _issue(report, code, f'Slide {index}: {sorted(missing)}', slide=index)
        for field, inventory in minimums.items():
            if field not in expected:
                continue
            count = expected[field]
            if type(count) is not int or count < 0:
                invalid(f'{field} on slide {index} must be a nonnegative integer.')
            elif page[inventory] < count:
                _issue(report, 'native_object_count_too_low', f'Slide {index}: {field} expected {count}, got {page[inventory]}', slide=index)
    unplanned = sorted(set(by_index) - seen)
    report['planned_slide_indices'] = sorted(seen)
    report['unplanned_slide_indices'] = unplanned
    report['plan_coverage'] = 'all_slides' if seen and not unplanned else ('partial' if seen else 'none')
    if unplanned:
        _issue(report, 'partial_plan_coverage', f'Slides without object-plan assertions: {unplanned}', 'warning')
    protected = plan.get('protected_parts', {})
    if not isinstance(protected, dict):
        invalid('protected_parts must map package part names to SHA-256 strings.')
        return
    names = set(z.namelist())
    for part, expected_hash in protected.items():
        if not isinstance(part, str) or not isinstance(expected_hash, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', expected_hash):
            invalid('Every protected part needs a package path and a 64-character SHA-256.')
        elif part not in names:
            _issue(report, 'protected_part_missing', part)
        elif hashlib.sha256(z.read(part)).hexdigest() != expected_hash.lower():
            _issue(report, 'protected_part_changed', part)


def inspect_deck(path, plan=None):
    """Return inventory and issues. Does not modify the input or call Office."""
    path = Path(path)
    report = {
        'schema_version': 1, 'input': str(path), 'scope': 'structure_only',
        'structural_status': 'fail', 'plan_checked': plan is not None,
        'plan_status': 'not_requested' if plan is None else 'not_completed',
        'plan_coverage': 'not_requested' if plan is None else 'none',
        'visual_validation': 'not_run', 'playback_validation': 'not_run',
        'slides': [], 'issues': [],
        'limits': [
            '原生对象数量不证明语义正确、数据可修改、全部内容可编辑或视觉合格。',
            '动画目标与进入分类只提供结构证据，不能证明具体时序正确或现场播放成功。',
            '不执行完整 Office XSD 校验；Strict 命名空间不受支持。',
            '部件哈希适用于完全锁定的部件；同页允许编辑区域需另做对象级比较。',
        ],
    }
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            if len(names) != len(z.namelist()):
                _issue(report, 'duplicate_zip_member', 'Package contains duplicate member names.')
            required = {'[Content_Types].xml', 'ppt/presentation.xml', 'ppt/_rels/presentation.xml.rels'}
            if not required <= names:
                _issue(report, 'invalid_package', 'Missing required PPTX parts: ' + ', '.join(sorted(required - names)))
                return report
            relations = _relationships(z, names, report)
            presentation = _xml(z, 'ppt/presentation.xml', report)
            if presentation is None:
                return report
            if presentation.tag != f"{{{NS['p']}}}presentation":
                _issue(report, 'unsupported_presentation_namespace', presentation.tag)
                return report
            ordered = presentation.findall('./p:sldIdLst/p:sldId', NS)
            if not ordered:
                _issue(report, 'empty_presentation', 'No slides in presentation order.')
            for index, sld_id in enumerate(ordered, 1):
                key = sld_id.get(f"{{{NS['r']}}}id")
                rel = relations.get('ppt/presentation.xml', {}).get(key, {})
                if rel.get('external') or not rel.get('type', '').endswith('/slide'):
                    _issue(report, 'invalid_slide_relationship', f'Slide {index}: {key}')
                    continue
                part = rel.get('target', '')
                root = _xml(z, part, report)
                if root is None:
                    continue
                if root.tag != f"{{{NS['p']}}}sld":
                    _issue(report, 'unsupported_slide_namespace', part)
                    continue
                report['slides'].append(_slide_inventory(root, part, index, relations.get(part, {}), report))
            if plan is not None:
                before = len(report['issues'])
                _check_plan(z, report, plan)
                report['plan_status'] = 'fail' if any(x['severity'] == 'error' for x in report['issues'][before:]) else 'pass'
            report['slide_count'] = len(report['slides'])
            report['summary'] = {
                key: sum(page[key] for page in report['slides'])
                for key in ('object_count', 'native_chart_count', 'native_table_count', 'picture_count', 'svg_picture_count')
            }
            report['structural_status'] = 'fail' if any(x['severity'] == 'error' for x in report['issues']) else 'pass'
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, ValueError, zlib.error) as exc:
        _issue(report, 'invalid_package', str(exc))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('deck', type=Path)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding='utf-8-sig')) if args.plan else None
        if args.plan and not isinstance(plan, dict):
            raise ValueError('--plan must contain a JSON object, not null or an array.')
        result = inspect_deck(args.deck, plan)
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            if args.output.resolve() == args.deck.resolve() or (args.plan and args.output.resolve() == args.plan.resolve()):
                raise ValueError('--output cannot overwrite deck or plan.')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload + '\n', encoding='utf-8')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        print(payload)
        return 0 if result['structural_status'] == 'pass' else 1
    except (OSError, ValueError) as exc:
        print(json.dumps({'structural_status': 'fail', 'issues': [{'code': 'invalid_input', 'severity': 'error', 'message': str(exc)}]}, ensure_ascii=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
