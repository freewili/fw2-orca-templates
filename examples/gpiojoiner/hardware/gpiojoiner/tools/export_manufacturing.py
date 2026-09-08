"""Export the reviewed PCB into Gerber, drill, position and drawing inputs.

Run with KiCad Python, after verify_project.py. No source CAD is regenerated.
"""
from pathlib import Path
import json
import hashlib
import math
import subprocess
import sys
import pcbnew as k

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/revA'
CLI=Path(sys.executable).with_name('kicad-cli.exe')


def run(*args):
    p=subprocess.run([str(CLI),*map(str,args)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    print(p.stdout.strip())


def export():
    verified=(ROOT/'reports/verification.md').read_text(encoding='utf-8')
    for name in ['gpiojoiner.kicad_sch','gpiojoiner.kicad_pcb','gpiojoiner.kicad_pro']:
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() in verified, 'Run fresh CAD verification: '+name
    drc=json.loads((ROOT/'reports/drc.json').read_text())
    assert not any(drc[x] for x in ['violations','unconnected_items','schematic_parity'])
    for d in ['gerbers','assembly','drawings','checks']: (OUT/d).mkdir(parents=True,exist_ok=True)
    board=k.LoadBoard(str(ROOT/'gpiojoiner.kicad_pcb'))
    run('pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts',
        '--use-drill-file-origin','--subtract-soldermask','--no-x2','--no-netlist',
        '--disable-aperture-macros','-o',OUT/'gerbers','gpiojoiner.kicad_pcb')
    # KiCad's generic job file says finish=None and includes line-width bounds.
    # Keep it as a build record; the supplied fabrication drawing specifies
    # ENIG and dimensions to the outline centerline.
    (OUT/'gerbers/gpiojoiner-job.gbrjob').replace(OUT/'checks/gpiojoiner-job.gbrjob')
    run('pcb','export','drill','--format','excellon','--drill-origin','plot',
        '--excellon-units','mm','--excellon-zeros-format','decimal','--excellon-separate-th',
        '--generate-report','--report-path',OUT/'checks/drill-report.txt',
        '-o',OUT/'gerbers','gpiojoiner.kicad_pcb')
    run('pcb','export','pos','--format','csv','--units','mm','--side','front','--exclude-dnp',
        '--use-drill-file-origin','-o',OUT/'checks/kicad-positions.csv','gpiojoiner.kicad_pcb')
    run('pcb','export','ipcd356','-o',OUT/'gerbers/gpiojoiner.d356','gpiojoiner.kicad_pcb')
    # Stencil omits optional DNP resistor apertures. Copper/mask is unchanged.
    for fp in board.GetFootprints():
        if fp.IsDNP():
            for pad in fp.Pads():
                layers=pad.GetLayerSet();layers.RemoveLayer(k.F_Paste);layers.RemoveLayer(k.B_Paste);pad.SetLayerSet(layers)
    temp=OUT/'checks/stencil.kicad_pcb';k.SaveBoard(str(temp),board)
    run('pcb','export','gerbers','--layers','F.Paste','--use-drill-file-origin',
        '--no-x2','--no-netlist','--disable-aperture-macros','-o',OUT/'checks',temp)
    (OUT/'gerbers/gpiojoiner-F_Paste.gtp').write_bytes((OUT/'checks/stencil-F_Paste.gtp').read_bytes())
    # Drawing coordinates retain KiCad's top-view XY convention. Assembly
    # exports use origin(85,215), X right, Y up, in millimeters.
    def xy(v):return [k.ToMM(v.x),k.ToMM(v.y)]
    geometry={'outline':[],'footprints':[],'origin':[85,215],'size_mm':[130,130]}
    for item in board.GetDrawings():
        if item.GetLayer()==k.Edge_Cuts:geometry['outline'].append([xy(item.GetStart()),xy(item.GetEnd())])
    holes=[]
    for fp in board.GetFootprints():
        pads=[]
        for pad in fp.Pads():
            drill=xy(pad.GetDrillSize());p=xy(pad.GetPosition())
            pads.append({'number':pad.GetNumber(),'xy':p,'size':xy(pad.GetSize()),'drill':drill,'net':pad.GetNetname()})
            if drill[0]: holes.append((fp.GetReference()+'.'+pad.GetNumber(),*p,drill[0]))
        geometry['footprints'].append({'ref':fp.GetReference(),'value':fp.GetValue(),'footprint':fp.GetFPIDAsString(),
            'xy':xy(fp.GetPosition()),'rotation':fp.GetOrientationDegrees()%360,'dnp':fp.IsDNP(),'pads':pads})
    for via in board.GetTracks():
        if type(via)==k.PCB_VIA:holes.append(('via',*xy(via.GetPosition()),k.ToMM(via.GetDrillValue())))
    nearest=min((math.hypot(a[1]-b[1],a[2]-b[2])-(a[3]+b[3])/2,a[0],b[0])
                 for i,a in enumerate(holes) for b in holes[i+1:])
    geometry['drill_count']=len(holes);geometry['minimum_hole_gap']=nearest
    geometry['holes']=[{'ref':h[0],'xy':list(h[1:3]),'diameter':h[3],'plated':not h[0].startswith('H')} for h in holes]
    geometry['source_sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        for name in ['gpiojoiner.kicad_pcb','gpiojoiner.kicad_sch','gpiojoiner.kicad_pro']}
    (OUT/'checks/geometry.json').write_text(json.dumps(geometry,indent=2),encoding='utf-8')
    print('Exported CAD manufacturing inputs;',len(holes),'holes; closest edge gap',nearest)


if __name__=='__main__':export()
