"""Independently parse exported CAM files and compare them with the CAD snapshot.

Requires gerbonara. Optional --dependencies points to a directory
containing these packages (keeps temporary dependencies outside the project).
"""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
import math
import sys
import warnings
from datetime import datetime, timezone

parser=argparse.ArgumentParser()
parser.add_argument('--dependencies',type=Path)
args=parser.parse_args()
if args.dependencies:sys.path.insert(0,str(args.dependencies))
from gerbonara import LayerStack, ipc356
from gerbonara.utils import MM

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/revA'
G=json.loads((OUT/'checks/geometry.json').read_text())
PARTS=json.loads((ROOT/'manufacturing/parts.json').read_text())
FPS={f['ref']:f for f in G['footprints']}
FITTED={r for p in PARTS['parts'] for r in p['refs']}
SMD={r for p in PARTS['parts'] if p['type']=='SMD' for r in p['refs']}
assert len(FITTED)==14 and len(SMD)==7
assert {f['ref'] for f in G['footprints'] if f['dnp']}==set(PARTS['do_not_populate'])
for name,digest in G['source_sha256'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'Stale export: '+name
    assert digest in (ROOT/'reports/verification.md').read_text(encoding='utf-8'), 'Unverified CAD: '+name

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    stack=LayerStack.open(OUT/'gerbers')
assert set(stack.graphic_layers)=={('top','copper'),('bottom','copper'),('top','mask'),
    ('bottom','mask'),('top','silk'),('bottom','silk'),('top','paste'),('mechanical','outline')}
assert len(stack.outline.objects)==12
assert stack.outline.bounding_box()==((-0.025,-0.025),(130.025,130.025))
def datum(p):return (p[0]-85,215-p[1])
def point(p):return tuple(round(x,3) for x in p)
def camxy(o):return (MM(o.x,o.unit),MM(o.y,o.unit))
for plated,layer,count in [(True,stack.drill_pth,158),(False,stack.drill_npth,4)]:
    assert len(layer.objects)==count
    expected=[(*datum(h['xy']),h['diameter']) for h in G['holes'] if h['plated']==plated]
    actual=[(*camxy(o),MM(o.aperture.diameter,o.aperture.unit)) for o in layer.objects]
    # Excellon decimals resolve 0.001 mm. Halfway values differ between
    # Python's tie-to-even and KiCad's integer-coordinate rounding.
    for e in expected:
        matches=[i for i,a in enumerate(actual) if max(abs(x-y) for x,y in zip(e,a))<=0.000501]
        assert len(matches)==1, 'Drill coordinate/diameter mismatch: '+str(e)
        actual.pop(matches[0])
    assert not actual, 'Unexpected exported drill hits'

paste=stack.graphic_layers[('top','paste')]
assert len(paste.objects)==18
def paste_center(o):
    # KiCad emits rounded paste apertures as regions with macros disabled.
    (x0,y0),(x1,y1)=o.bounding_box(unit=MM)
    return ((x0+x1)/2,(y0+y1)/2)
remaining=[paste_center(o) for o in paste.objects]
for ref in SMD:
    for pad in FPS[ref]['pads']:
        e=datum(pad['xy'])
        matches=[i for i,a in enumerate(remaining) if max(abs(x-y) for x,y in zip(e,a))<0.00001]
        assert len(matches)==1, 'Fitted stencil mismatch: '+ref+'.'+pad['number']
        remaining.pop(matches[0])
assert not remaining
for ref in PARTS['do_not_populate']:
    for p in FPS[ref]['pads']:
        assert point(datum(p['xy'])) not in {point(paste_center(o)) for o in paste.objects}

netlist=ipc356.Netlist.open(OUT/'gerbers/gpiojoiner.d356')
assert len(netlist.test_records)==194
assert sum(r.is_via for r in netlist.test_records)==52
records={(r.ref_des,r.pin):r for r in netlist.test_records if not r.is_via and not r.ref_des.startswith('H')}
assert len(records)==138
net_mapping=collections.defaultdict(set)
for ref,fp in FPS.items():
    if ref.startswith('H'):continue
    for pad in fp['pads']:
        rec=records[(ref,pad['number'])]
        expected=datum(pad['xy']);actual=camxy(rec)
        assert max(abs(a-b) for a,b in zip(expected,actual))<=0.0013, 'IPC origin/pad mismatch'
        net_mapping[rec.net_name].add(pad['net'])
assert all(len(nets)==1 for nets in net_mapping.values()), 'IPC net-name truncation creates an alias'
assert len(net_mapping)==len({p['net'] for fp in FPS.values() if not fp['ref'].startswith('H') for p in fp['pads']}), 'IPC split or merged net'

def rows(name):
    with (OUT/'assembly'/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
for vendor in ['jlcpcb','pcbway']:
    bom=rows(vendor+'-bom.csv');assert len(bom)==7
    refs=[r for row in bom for r in row['Designator'].split(',')]
    assert len(refs)==14 and set(refs)==FITTED
    for row,part in zip(bom,PARTS['parts']):
        assert row['Comment' if vendor=='jlcpcb' else 'Manufacturer Part Number']==part['mpn']
        assert row['LCSC Part #']==part['lcsc'] and row['Footprint']==part['package']
        if vendor=='pcbway':assert int(row['Quantity'])==len(part['refs'])
    expected_cpl=SMD if vendor=='pcbway' else FITTED
    cpl=rows(vendor+'-cpl.csv');assert len(cpl)==len(expected_cpl)
    assert {r['Designator'] for r in cpl}==expected_cpl
    for row in cpl:
        fp=FPS[row['Designator']];x,y=datum(fp['xy'])
        assert abs(float(row['Mid X'])-x)<1e-6 and abs(float(row['Mid Y'])-y)<1e-6
        assert float(row['Rotation'])==fp['rotation'] and row['Layer']=='Top'
        assert 0<=x<=130 and 0<=y<=130

for side in ['top','bottom']:
    svg=str(stack.to_pretty_svg(side=side))
    (OUT/f'checks/gerber-{side}.svg').write_text(svg,encoding='utf-8')
warning_text='\n'.join('- '+str(w.message).replace(str(OUT/'gerbers')+'\\','') for w in caught)
report=f'''# Rev A manufacturing export checks

Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}.
Independent Gerbonara CAM parser compared with the verified KiCad geometry.

- PASS: source schematic, PCB and project hashes match fresh CAD verification.
- PASS: eight Gerber graphic layers; twelve outline edges; 130 x 130 mm centerline bounds.
- PASS: all 162 drill positions and diameters match CAD within 0.000501 mm (158 plated, four non-plated).
- PASS: minimum hole edge gap {G['minimum_hole_gap'][0]:.3f} mm.
- PASS: 18 stencil apertures match the seven fitted SMD parts; all four DNP resistor positions omitted.
- PASS: IPC-D-356 parses 194 records: 138 electrical pads, 52 vias, four mounting holes.
- PASS: all 138 IPC pad coordinates match CAD within 0.0013 mm; exported net names preserve connectivity groups.
- PASS: both supplier BOMs contain seven exact-MPN lines, 14 fitted references and no DNP/TP/holes.
- PASS: JLCPCB CPL includes 14 fitted parts; PCBWay CPL includes seven SMD parts per its published file requirements. All listed coordinates, sides and rotations match CAD; common Gerber/drill/CPL datum.
- Generated independent top/bottom Gerber SVG previews for visual review. Use render_cam.mjs for PNGs (SVG filters require a compatible renderer).

The native IPC-D-356 uses 0.0001-inch resolution; its datum matches the metric Gerbers.
CPL values remain KiCad footprint datums; manufacturer placement overlays need review,
especially the connector bodies, switch and polarized parts. No assembly-machine
rotation corrections are guessed here. This is prototype quotation data; manufacturer
DFM acceptance, physical mating, EEPROM identity and bench operation are unverified.

## Parser observations

{warning_text or 'No parser warnings.'}

KiCad emits G90 after the Excellon header. Gerbonara accepts and applies this
absolute-coordinate statement, while reporting its header placement. All drill
hits parsed and matched the CAD snapshot; the native KiCad drill files are retained.
'''
(OUT/'manufacturing-checks.md').write_text(report,encoding='utf-8')
print('PASS: Gerber layers/outline, all drills, fitted stencil, IPC nets/pads, exact BOMs and CPLs; SVG previews generated.')
