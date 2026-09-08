"""Prepare rev A silkscreen and fabrication origin for prototype production.

Run with KiCad Python. Electrical geometry is required to remain identical.
"""
from pathlib import Path
import json
import pcbnew as k

ROOT=Path(__file__).resolve().parents[1]


def electrical(board):
    return sorted((f.GetReference(),p.GetNumber(),p.GetNetname(),
                   p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y,
                   p.GetDrillSize().x,p.GetDrillSize().y)
                  for f in board.GetFootprints() for p in f.Pads()), sorted(
        (t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,
         t.GetEnd().x,t.GetEnd().y,
         t.GetWidth(k.F_Cu) if type(t)==k.PCB_VIA else t.GetWidth()) for t in board.GetTracks())


def prepare():
    path=ROOT/'gpiojoiner.kicad_pcb';board=k.LoadBoard(str(path));before=electrical(board)
    count=0
    for item in board.GetDrawings():
        if type(item)==k.PCB_TEXT and item.GetLayer() in [k.F_SilkS,k.B_SilkS]:
            if item.GetTextSize().x<k.FromMM(1):
                item.SetTextSize(k.VECTOR2I(k.FromMM(1),k.FromMM(1)));count+=1
    for fp in board.GetFootprints():
        for item in fp.GraphicalItems():
            if type(item)==k.PCB_SHAPE and item.GetLayer() in [k.F_SilkS,k.B_SilkS]:
                if item.GetWidth()<k.FromMM(.15): item.SetWidth(k.FromMM(.15));count+=1
    # Match project-local library silk widths to their placed footprints.
    for lib in ROOT.glob('*.pretty'):
        for mod in lib.glob('*.kicad_mod'):
            fp=k.FootprintLoad(str(lib),mod.stem)
            changed=False
            for item in fp.GraphicalItems():
                if type(item)==k.PCB_SHAPE and item.GetLayer() in [k.F_SilkS,k.B_SilkS] and item.GetWidth()<k.FromMM(.15):
                    item.SetWidth(k.FromMM(.15));changed=True
            if changed:k.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib),fp)
    board.GetDesignSettings().SetAuxOrigin(k.VECTOR2I(k.FromMM(85),k.FromMM(215)))
    assert before==electrical(board),'Preparation changed electrical geometry'
    k.SaveBoard(str(path),board)
    pro=ROOT/'gpiojoiner.kicad_pro';data=json.loads(pro.read_text())
    rules=data['board']['design_settings']['rules'];rules['min_text_height']=1.0;rules['min_text_thickness']=.15
    pro.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('Manufacturing preparation:',count,'silk changes; electrical geometry unchanged; origin at bounding-box lower left')


if __name__=='__main__':prepare()
