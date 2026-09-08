"""Independent acceptance audit of KiCad XML, based on DESIGN.md and PINOUTS.md.

No imports from the generator: this checks the actual exported CAD connectivity.
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def audit(path):
    if not path.is_file():
        raise AssertionError(f"Missing exported KiCad netlist: {path}")
    tree = ET.parse(path)
    parts = {c.attrib['ref']: c for c in tree.findall('./components/comp')}
    expected_refs={f'J{i}' for i in range(1,7)} | {f'R{i}' for i in range(1,9)} | {f'TP{i}' for i in range(1,7)} | {'U1','D1','C1','SW1'}
    assert set(parts)==expected_refs, f"Unexpected/missing physical components: {set(parts)^expected_refs}"
    expected_footprints={
        'U1':'Package_TO_SOT_SMD:SOT-23-5',
        'D1':'Package_TO_SOT_SMD:SOT-23',
        'SW1':'GPIOJoiner:SW_JS202011CQN',
        'C1':'Capacitor_SMD:C_0603_1608Metric',
    }
    expected_footprints.update({f'J{i}':'GPIOJoiner:ORCA_10_RA' if i in (2,4) else 'GPIOJoiner:ORCA_20_RA' for i in range(1,7)})
    expected_footprints.update({f'R{i}':'Resistor_SMD:R_0603_1608Metric' for i in range(1,9)})
    expected_footprints.update({f'TP{i}':'TestPoint:TestPoint_Pad_D1.5mm' for i in range(1,7)})
    for ref,footprint in expected_footprints.items():
        assert parts[ref].findtext('footprint') == footprint, f"Wrong footprint {ref}"
    nets = {}
    for n in tree.findall('./nets/net'):
        for p in n.findall('node'):
            key = (p.attrib['ref'], p.attrib['pin'])
            assert key not in nets, f"Duplicate pin {key}"
            nets[key] = n.attrib['code']
    count = 1+len(expected_footprints)
    def pin(ref, num):
        assert (ref,str(num)) in nets, f"Missing {ref}.{num}"
        return nets[(ref,str(num))]
    def same(*pins):
        nonlocal count
        assert len({pin(*p) for p in pins}) == 1, f"Not connected: {pins}"
        count += 1
    def different(*pins):
        nonlocal count
        values = [pin(*p) for p in pins]
        assert len(set(values)) == len(values), f"Unexpected short: {pins}"
        count += 1
    # Four allowed combinations. No physical-star assumption is used.
    mapping = {1:1,3:14,5:9,7:11,8:8,9:5,10:10,11:7,12:13,13:12,14:3,15:15,19:19,20:20}
    for a in ('J1','J5'):
        for b in ('J3','J6'):
            for pa,pb in mapping.items(): same((a,pa),(b,pb))
            different((a,17),(b,17))
    for refs,side,tp in [(('J1','J5'),'A','TP1'),(('J3','J6'),'B','TP2')]:
        for p in (1,3,4,5,7,8,9,10,11,12,13,14,15,17,19,20): same((refs[0],p),(refs[1],p))
        same((refs[0],17),(tp,1))
    # Supply isolation and no copper ties through passive isolation components.
    different(('J1',6),('J3',6),('J5',6),('J6',6),('U1',4),('J1',4),('J3',4),('J1',19))
    for ref in ('J1','J3','J5','J6'):
        k = nets.get((ref,'2'))
        assert k is None or sum(v == k for v in nets.values()) == 1, f"5V output connected: {ref}"
    for ref in ('J5','J6'):
        for p in (16,18):
            k=nets.get((ref,str(p)))
            assert k is None or sum(v == k for v in nets.values()) == 1, f"OG SWD connected: {ref}.{p}"
    same(('J1',16),('J3',16),('R7',1),('R8',1))
    same(('J1',18),('J3',18),('R7',2),('R8',2))
    different(('J1',16),('J1',18),('J1',19))
    # DPDT pin assignment and simulated contact closures in both modes.
    same(('SW1',2),('J1',4),('J5',4))
    same(('SW1',5),('J3',4),('J6',4))
    same(('SW1',1),('SW1',4))
    same(('SW1',3),('J5',6))
    same(('SW1',6),('J6',6))
    for mode,contacts in [('FW2/mixed',((2,1),(5,4))),('OG/OG',((2,3),(5,6)))]:
        parent={v:v for v in nets.values()}
        def root(x):
            while parent[x] != x: x=parent[x]
            return x
        for a,b in contacts: parent[root(pin('SW1',a))]=root(pin('SW1',b))
        eq=lambda a,b: root(pin(*a)) == root(pin(*b))
        assert eq(('J1',4),('J3',4)) == (mode=='FW2/mixed'), f"VREF state {mode}"
        assert eq(('J1',4),('J5',6)) == (mode=='OG/OG'), f"A reference state {mode}"
        assert eq(('J3',4),('J6',6)) == (mode=='OG/OG'), f"B reference state {mode}"
        rails=[('J1',6),('J3',6),('J5',6),('J6',6)]
        assert len({root(pin(*p)) for p in rails}) == 4, f"Supply short in {mode}"
        count+=4
    # I2C1 direct copper, EEPROM package pins, diode orientation and bypass.
    same(('J2',7),('J4',7),('U1',1),('R5',2))
    same(('J2',9),('J4',9),('U1',3),('R6',2))
    same(('J1',6),('D1',1))
    same(('J3',6),('D1',2))
    same(('D1',3),('U1',4),('C1',1),('R5',1),('R6',1),('TP6',1))
    same(('J1',19),('J1',20),('J3',19),('J3',20),('J5',19),('J5',20),('J6',19),('J6',20),('J2',1),('J4',1),('U1',2),('U1',5),('C1',2),('R2',2),('R4',2),('TP5',1))
    for a,b,upper,lower,tp in [('J2','J4','R1','R2','TP3'),('J4','J2','R3','R4','TP4')]:
        same((a,5),(b,8))
        same((a,3),(b,6))
        same((a,10),(upper,1))
        same((upper,2),(lower,1),(b,4))
        different((a,10),(b,4),('J1',19))
        same((a,2),(tp,1))
    different(('J2',2),('J4',2),('J2',3),('J4',3),('J2',5),('J4',5))
    expected={'U1':'24LC02BT-E/OT','D1':'BAT54C','C1':'100nF','SW1':'JS202011CQN'}
    expected.update({f'R{i}':'10k 0.1%' for i in range(1,5)})
    expected.update({'R5':'4.7k','R6':'4.7k','R7':'120','R8':'120'})
    for ref,value in expected.items():
        assert parts[ref].findtext('value') == value, f"Wrong value {ref}"
        dnp = parts[ref].find("property[@name='dnp']") is not None
        assert dnp == (ref in ('R5','R6','R7','R8')), f"Wrong DNP {ref}"
        count+=2
    # Exact copper membership also catches extra unintended branches, not just missing pairs.
    expected_groups = [
        'J1.1 J3.1 J5.1 J6.1', 'J1.3 J5.3 J3.14 J6.14',
        'J1.14 J5.14 J3.3 J6.3', 'J1.5 J5.5 J3.9 J6.9',
        'J1.9 J5.9 J3.5 J6.5', 'J1.7 J5.7 J3.11 J6.11',
        'J1.11 J5.11 J3.7 J6.7', 'J1.8 J3.8 J5.8 J6.8',
        'J1.10 J3.10 J5.10 J6.10', 'J1.12 J5.12 J3.13 J6.13',
        'J1.13 J5.13 J3.12 J6.12', 'J1.15 J3.15 J5.15 J6.15',
        'J1.17 J5.17 TP1.1','J3.17 J6.17 TP2.1',
        'J1.4 J5.4 SW1.2','J3.4 J6.4 SW1.5','SW1.1 SW1.4',
        'J1.6 D1.1','J3.6 D1.2','J5.6 SW1.3','J6.6 SW1.6',
        'J1.16 J3.16 R7.1 R8.1','J1.18 J3.18 R7.2 R8.2',
        'J2.7 J4.7 U1.1 R5.2','J2.9 J4.9 U1.3 R6.2',
        'D1.3 U1.4 C1.1 R5.1 R6.1 TP6.1',
        'J2.3 J4.6','J2.5 J4.8','J4.3 J2.6','J4.5 J2.8',
        'J2.10 R1.1','R1.2 R2.1 J4.4','J4.10 R3.1','R3.2 R4.1 J2.4',
        'J2.2 TP3.1','J4.2 TP4.1',
        'J1.19 J1.20 J3.19 J3.20 J5.19 J5.20 J6.19 J6.20 J2.1 J4.1 U1.2 U1.5 C1.2 R2.2 R4.2 TP5.1',
    ]
    for group in expected_groups:
        want={tuple(x.split('.')) for x in group.split()}
        key=pin(*next(iter(want)))
        got={p for p,n in nets.items() if n==key and not p[0].startswith('#')}
        assert got==want, f"Unexpected net membership: wanted {want}; got {got}"
        count+=1
    print(f"PASS: {count} connection/value assertions; four device pairings, both VREF modes, 37 exact copper-net groups.")

if __name__ == '__main__':
    try: audit(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'reports/netlist.xml')
    except (AssertionError, ET.ParseError, KeyError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
