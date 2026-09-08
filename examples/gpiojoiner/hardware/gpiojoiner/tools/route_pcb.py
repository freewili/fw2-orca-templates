"""Route this project locally with Freerouting, then refill the ground pours.

Run with KiCad Python. JAVA and FREEROUTING_JAR are explicit arguments;
no remote routing service is used. Input board must have no existing tracks.
"""
from pathlib import Path
import argparse
import json
import re
import subprocess
import uuid
import pcbnew as k

ROOT=Path(__file__).resolve().parents[1]


def route(java,jar):
    path=ROOT/'gpiojoiner.kicad_pcb';board=k.LoadBoard(str(path))
    assert not list(board.GetTracks()),'Existing routing found; refuse to overwrite manual work'
    out=ROOT/'reports/routing';out.mkdir(exist_ok=True)
    dsn=out/'gpiojoiner.dsn';ses=out/'gpiojoiner.ses'
    # Route the ground connections explicitly; refill the original pours after
    # import. DSN plane declarations otherwise hide disconnected ground pads.
    assert k.ExportSpecctraDSN(board,str(dsn)),'DSN export failed'
    data=dsn.read_text(encoding='utf-8')
    # These generated planes have exactly one polygon and no nested holes.
    # Editing the export also avoids removing owned SWIG zone objects.
    data,n=re.subn(r'\s*\(plane GND \(polygon[^()]*\)\)', '',data)
    assert n==2,'Expected two exported ground polygons'
    # KiCad's DSN omits its copper-edge constraint. Give the boundary its own
    # clearance class, as supported by Freerouting's SPECCTRA parser.
    data,n=re.subn(r'(\(boundary\s*\(path pcb.*?\))\s*\)',
                   r'\1 (clearance_class board_edge))',data,count=1,flags=re.S)
    assert n==1,'Expected one DSN outline'
    data=data.replace('(clearance 50 (type smd_smd))',
                      '(clearance 150 (type smd_smd))\n'
                      '      (clearance 350 (type default_board_edge))')
    dsn.write_text(data,encoding='utf-8')
    config=out/'engine-data';config.mkdir(exist_ok=True)
    (config/'freerouting.json').write_text(json.dumps({
        'version':'2.2.4','profile':{'id':str(uuid.uuid4()),'email':'',
                                    'allow_telemetry':False,'allow_contact':False},
        'gui':{'enabled':False},'api_server':{'enabled':False},
        'usage_and_diagnostic_data':{'disable_analytics':True},
        'feature_flags':{'save_jobs':False}}),encoding='utf-8')
    command=[str(java),'-jar',str(jar),'-de',str(dsn),'-do',str(ses),
             '-mp','40','-mt','2','-da','--gui.enabled=false','--api_server.enabled=false',
             '--profile.allow_telemetry=false','--profile.allow_contact=false',
             '--feature_flags.save_jobs=false','--user_data_path='+str(out/'engine-data')]
    if ses.exists(): ses.unlink()
    with (out/'freerouting.log').open('w',encoding='utf-8') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=600)
    assert result.returncode==0,f'Router exit {result.returncode}; see freerouting.log'
    assert ses.exists(),'Router did not produce SES'
    assert k.ImportSpecctraSES(board,str(ses)),'SES import failed'
    k.ZONE_FILLER(board).Fill(board.Zones())
    k.SaveBoard(str(path),board)
    print('Imported routing and filled GND zones;',len(list(board.GetTracks())),'track/via items')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java',type=Path,required=True);ap.add_argument('--jar',type=Path,required=True)
    args=ap.parse_args();route(args.java,args.jar)
