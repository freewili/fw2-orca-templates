"""Package inspected prototype deliverables; no vendor upload or order is made."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/revA'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
geometry=json.loads((OUT/'checks/geometry.json').read_text())
for name,digest in geometry['source_sha256'].items():assert sha(ROOT/name)==digest, 'Stale CAD: '+name
assert (OUT/'manufacturing-checks.md').stat().st_mtime>max(
    p.stat().st_mtime for p in [*OUT.joinpath('gerbers').iterdir(),*OUT.joinpath('assembly').glob('*.csv')])
for p in (OUT/'checks').glob('gerber-*.png'):
    assert p.stat().st_mtime>(OUT/'manufacturing-checks.md').stat().st_mtime, 'Render current Gerbers'

cam_names={'gpiojoiner-F_Cu.gtl','gpiojoiner-B_Cu.gbl','gpiojoiner-F_Mask.gts',
    'gpiojoiner-B_Mask.gbs','gpiojoiner-F_Silkscreen.gto','gpiojoiner-B_Silkscreen.gbo',
    'gpiojoiner-Edge_Cuts.gm1','gpiojoiner-F_Paste.gtp','gpiojoiner-PTH.drl',
    'gpiojoiner-NPTH.drl','gpiojoiner.d356'}
assert {p.name for p in (OUT/'gerbers').iterdir()}==cam_names
cam_zip=OUT/'gpiojoiner-revA-gerbers.zip'
with zipfile.ZipFile(cam_zip,'w',zipfile.ZIP_DEFLATED) as z:
    for name in sorted(cam_names):z.write(OUT/'gerbers'/name,name)
with zipfile.ZipFile(cam_zip) as z:assert z.testzip() is None and set(z.namelist())==cam_names

(OUT/'drawings').mkdir(exist_ok=True)
shutil.copyfile(ROOT/'previews/schematic.pdf',OUT/'drawings/gpiojoiner-revA-schematic.pdf')
for side in ['top','bottom']:
    shutil.copyfile(OUT/f'checks/gerber-{side}.png',OUT/f'drawings/gerber-{side}.png')
shutil.copyfile(ROOT/'manufacturing/parts.json',OUT/'parts.json')
cad_report=(ROOT/'reports/verification.md').read_text(encoding='utf-8')
cad_report=cad_report.replace('[circuit-review.md](circuit-review.md)',
    '`hardware/gpiojoiner/reports/circuit-review.md` in the source project')
cad_report=cad_report.replace('[setup and bench requirements](../README.md)',
    '[setup and bench requirements](README.md#after-the-prototypes-arrive)')
(OUT/'cad-verification.md').write_text(cad_report,encoding='utf-8')
(OUT/'source-cad-sha256.json').write_text(json.dumps(geometry['source_sha256'],indent=2)+'\n',encoding='utf-8')
files=[OUT/'README.md',cam_zip,OUT/'parts.json',OUT/'source-cad-sha256.json',
       OUT/'cad-verification.md',OUT/'manufacturing-checks.md',
       *sorted((OUT/'assembly').glob('*.csv')),*sorted((OUT/'drawings').glob('*'))]
assert len(files)==14
manifest=OUT/'SHA256SUMS.txt'
manifest.write_text(''.join(f'{sha(p)}  {p.relative_to(OUT).as_posix()}\n' for p in files),encoding='utf-8')
assembly_zip=OUT/'gpiojoiner-revA-assembly.zip'
with zipfile.ZipFile(assembly_zip,'w',zipfile.ZIP_DEFLATED) as z:
    for p in [*files,manifest]:z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(assembly_zip) as z:
    assert z.testzip() is None and len(z.namelist())==15
    assert not any('checks/' in n or 'stencil.kicad' in n for n in z.namelist())
    for p in files:assert hashlib.sha256(z.read(p.relative_to(OUT).as_posix())).hexdigest()==sha(p)
(OUT/'ZIP-SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in [cam_zip,assembly_zip]),encoding='utf-8')
for p in [cam_zip,assembly_zip]:print(f'PASS: {p.name}: {p.stat().st_size:,} bytes; archive CRC and content hashes verified')
