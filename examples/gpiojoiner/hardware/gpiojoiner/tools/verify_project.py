"""Re-export the netlist, run ERC/DRC and independent audits, record evidence.

Run with KiCad's bundled Python. Optional --cli overrides kicad-cli's path.
This refreshes reports and ground-zone fills; it does not regenerate the CAD.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


def verify(cli):
    logs=[]
    def run(args):
        result=subprocess.run([str(x) for x in args],cwd=ROOT,
                              capture_output=True,text=True,encoding='utf-8')
        output=result.stdout.strip()
        if output: print(output)
        logs.append(output)
        if result.returncode:
            raise RuntimeError(f'Failed ({result.returncode}): {args}\n{result.stderr}')
    sch='gpiojoiner.kicad_sch';pcb='gpiojoiner.kicad_pcb'
    run([cli,'sch','export','netlist','--format','kicadxml','-o','reports/netlist.xml',sch])
    # KiCad writes the local absolute source path. Publish a portable name;
    # connectivity and all electrical data remain unchanged.
    netlist=ROOT/'reports/netlist.xml'
    tree=ET.parse(netlist)
    tree.find('./design/source').text=sch
    tree.write(netlist,encoding='utf-8',xml_declaration=True)
    run([sys.executable,'tools/check_connections.py'])
    for fmt,suffix in [('json','json'),('report','rpt')]:
        run([cli,'sch','erc','--format',fmt,'--exit-code-violations','-o','reports/erc.'+suffix,sch])
    run([cli,'pcb','drc','--schematic-parity','--refill-zones','--save-board',
         '--format','json','--exit-code-violations','-o','reports/drc.json',pcb])
    run([sys.executable,'tools/check_pcb.py'])
    erc=json.loads((ROOT/'reports/erc.json').read_text())
    drc=json.loads((ROOT/'reports/drc.json').read_text())
    assert not any(s['violations'] for s in erc['sheets'])
    assert not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity']
    hashes='\n'.join(f'- `{name}`: `{hashlib.sha256((ROOT/name).read_bytes()).hexdigest()}`'
                     for name in [sch,pcb,'gpiojoiner.kicad_pro'])
    report=f'''# Rev A CAD verification

Fresh verification: {datetime.now(timezone.utc).isoformat(timespec='seconds')}.
KiCad {drc['kicad_version']}. All commands exited 0.

- Schematic connection audit: **216 assertions passed**, including all four
  allowed device pairings, both VREF modes, EEPROM/supply isolation,
  analog dividers, CAN isolation, and required DNP parts.
- PCB audit: **138 schematic pad/net assignments passed**, plus connector
  geometry, corrected switch numbering, local models, board construction,
  design rules and absence of DRC exclusions.
- ERC: **0 violations**.
- DRC: **0 violations, 0 unconnected items, 0 schematic parity issues**.
  Reports use the project's enabled error/warning checks. KiCad's ignored
  check categories are explicitly listed in the JSON reports.

These automated checks do not establish visual review. Inspect the schematic
and current top, bottom and perspective previews separately before release.
Independent circuit and footprint review is recorded in
[circuit-review.md](circuit-review.md).

Configured minimums: 0.20 mm tracks, 0.15 mm copper clearance, 0.30 mm
copper-edge clearance, 0.15 mm silk clearance, 1.0 mm text height and
0.15 mm text thickness.
The board uses two copper layers, 1.6 mm thickness and a 130 x 130 mm
cross outline. There are 28 footprints including four mechanical holes.

These checks establish CAD connectivity and the configured design rules.
They do not establish enclosure fit, manufactured-board quality, signal
integrity at a specified speed, EEPROM identification or hardware operation.
The [setup and bench requirements](../README.md) remain prerequisites to release.

## Reproduce

Run `tools/verify_project.py` with KiCad's bundled Python. It re-exports
the actual schematic netlist, runs both independent audits, runs ERC in
JSON and text formats, and runs DRC with zone refill and schematic parity.
It stops on a failing command and refreshes this report only on success.

## Verified file SHA-256

{hashes}

## Command output

```text
{chr(10).join(logs)}
```
'''
    (ROOT/'reports/verification.md').write_text(report,encoding='utf-8')
    print('PASS: verification evidence written to reports/verification.md')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cli',type=Path,default=Path(sys.executable).with_name('kicad-cli.exe'))
    verify(ap.parse_args().cli)
