"""Audit exported schematic nets against the PCB, plus docking geometry.

Run with KiCad's bundled Python after generating or editing the PCB.
ERC and DRC are complementary checks and must also be run through kicad-cli.
"""
from pathlib import Path
import math
import json
import xml.etree.ElementTree as ET
import pcbnew

ROOT = Path(__file__).resolve().parents[1]


def check():
    pcb = ROOT / 'gpiojoiner.kicad_pcb'
    assert pcb.exists(), 'PCB has not been created'
    board = pcbnew.LoadBoard(str(pcb))
    xml = ET.parse(ROOT / 'reports/netlist.xml').getroot()
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    expected = {}
    for net in xml.findall('./nets/net'):
        for node in net.findall('node'):
            expected[node.get('ref'), node.get('pin')] = net.get('name')
    checked = 0
    for comp in xml.findall('./components/comp'):
        ref = comp.get('ref')
        assert ref in fps, f'Missing footprint {ref}'
        fp = fps[ref]
        actual = {pad.GetNumber(): pad.GetNetname() for pad in fp.Pads()}
        for (r, pin), net in expected.items():
            if r == ref:
                assert actual.get(pin) == net, f'{ref}.{pin}: {actual.get(pin)} != {net}'
                checked += 1
        assert fp.GetValue() == comp.findtext('value'), f'{ref} value mismatch'
        assert fp.GetFPIDAsString() == comp.findtext('footprint'), f'{ref} footprint mismatch'
    for ref, count in [('J1',20),('J2',10),('J3',20),('J4',10),('J5',20),('J6',20)]:
        pads = list(fps[ref].Pads())
        assert {p.GetNumber() for p in pads} == {str(n) for n in range(1,count+1)}
        assert all(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for p in pads), ref
    for a,b in [('J1','J2'),('J3','J4')]:
        p,q = fps[a].GetPosition(),fps[b].GetPosition()
        assert math.isclose(pcbnew.ToMM(math.hypot(p.x-q.x,p.y-q.y)),26.72,abs_tol=.00001)
    assert fps['J1'].GetPosition().x < fps['J3'].GetPosition().x
    assert fps['J5'].GetPosition().y < fps['J6'].GetPosition().y
    assert [fps[r].GetOrientationDegrees()%360 for r in ['J1','J3','J5','J6']] == [0,180,270,90]
    switch_pads = {p.GetNumber():p.GetPosition() for p in fps['SW1'].Pads()}
    assert switch_pads['1'].x == switch_pads['4'].x, 'SW1 must have parallel numbered rows'
    assert switch_pads['3'].x == switch_pads['6'].x, 'SW1 second row is reversed'
    for ref in ['R5','R6','R7','R8']:
        assert fps[ref].IsDNP(), f'{ref} must be DNP'
    assert board.GetCopperLayerCount() == 2
    assert math.isclose(pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness()),1.6)
    assert all(f'H{i}' in fps for i in range(1,5))
    setup=json.loads((ROOT/'gpiojoiner.kicad_pro').read_text(encoding='utf-8'))['board']['design_settings']
    for key,value in {'min_clearance':.15,'min_track_width':.2,'min_copper_edge_clearance':.3,
                      'min_silk_clearance':.15,'min_text_height':1.0,'min_text_thickness':.15}.items():
        assert math.isclose(setup['rules'][key],value),f'Unexpected design rule: {key}'
    assert not setup.get('drc_exclusions'), 'Unexpected DRC exclusions'
    for fp in fps.values():
        for model in fp.Models():
            path = model.m_Filename.replace('${KIPRJMOD}',str(ROOT))
            assert Path(path).exists(), f'Missing model {model.m_Filename}'
    print(f'PASS: {checked} schematic pad/net assignments; 6 docking connectors; '
          'FW2 spacing/orientation; corrected switch; DNPs; 4 holes; local models.')


if __name__ == '__main__':
    check()
