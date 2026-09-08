"""Build the review PCB from the *exported schematic* netlist.

Run with KiCad's Python. Rebuilding overwrites the generated PCB, including
manual routing; use the explicit --rebuild flag. Footprints/models are local.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import tempfile
import uuid
import xml.etree.ElementTree as ET
import pcbnew as k

ROOT = Path(__file__).resolve().parents[1]
KICAD = Path(__import__('os').environ.get('KICAD_INSTALL', 'C:/Program Files/KiCad/10.0'))
LIBS = KICAD/'share/kicad/footprints'
MODELS = KICAD/'share/kicad/3dmodels'
NS = uuid.UUID('645ea78b-7034-4acf-ae68-a4d043649930')
OUTLINE = [(85,110),(110,110),(110,85),(190,85),(190,110),(215,110),
           (215,190),(190,190),(190,215),(110,215),(110,190),(85,190)]
PLACEMENT = {
    'J1':(88,139.82,0), 'J2':(88,166.54,0),
    'J3':(212,160.18,180), 'J4':(212,133.46,180),
    'J5':(150,88,270), 'J6':(150,212,90),
    'SW1':(147.5,147,0), 'U1':(151,164,0), 'D1':(144,164,0),
    'C1':(155,164,90), 'R5':(146,174,90), 'R6':(151,174,90),
    'R1':(199,136,0),'R2':(203,136,90),
    'R3':(100,164,180),'R4':(96,164,90),
    'R7':(97,131,90), 'R8':(203,169,90),
    'TP1':(121,150,0),'TP2':(179,150,0),
    'TP3':(98,177,0),'TP4':(202,123,0),
    'TP5':(157,172,0),'TP6':(141,172,0),
}


def v(x,y): return k.VECTOR2I(k.FromMM(x),k.FromMM(y))
def uid(*parts): return k.KIID(str(uuid.uuid5(NS,'/'.join(map(str,parts)))))


def line(parent,a,b,layer,width=.15):
    item = k.PCB_SHAPE(parent)
    item.SetShape(k.SHAPE_T_SEGMENT); item.SetStart(v(*a)); item.SetEnd(v(*b))
    item.SetLayer(layer); item.SetWidth(k.FromMM(width)); parent.Add(item)
    return item


def rect(parent,x1,y1,x2,y2,layer,width=.05):
    for a,b in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:
        line(parent,a,b,layer,width)


def localize_models(fp):
    models = list(fp.Models())
    for model in models:
        # Only the installed KiCad model macro is accepted here.
        source = re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}',MODELS.as_posix(),model.m_Filename)
        source = Path(source)
        if not source.exists():
            raise FileNotFoundError(f'Missing model: {source}')
        target = ROOT/'models'/source.name
        target.parent.mkdir(exist_ok=True)
        if not target.exists(): shutil.copy2(source,target)
        model.m_Filename = '${KIPRJMOD}/models/'+source.name
    fp.Models().clear()
    for model in models: fp.Add3DModel(model)


def save_lib(fp,lib,name):
    directory = ROOT/(lib+'.pretty')
    directory.mkdir(exist_ok=True)
    fp.SetPosition(v(0,0)); fp.SetOrientationDegrees(0)
    fp.SetFPIDAsString(f'{lib}:{name}')
    fp.SetReference('REF**'); fp.SetValue(name)
    for item in fp.GraphicalItems():
        if type(item)==k.PCB_SHAPE and item.GetLayer() in [k.F_SilkS,k.B_SilkS] and item.GetWidth()<k.FromMM(.15):
            item.SetWidth(k.FromMM(.15))
    # Empty new libraries cannot be auto-detected by KiCad 10's wrapper.
    plugin = k.PCB_IO_KICAD_SEXPR()
    plugin.FootprintSave(str(directory),fp)


def make_libraries(reference):
    source = k.LoadBoard(str(reference))
    for original in source.GetFootprints():
        count = len(list(original.Pads()))
        if count not in [10,20]: continue
        fp = original
        fp.SetPosition(v(0,0)); fp.SetOrientationDegrees(0)
        fp.Models().clear()
        # Keep the source corner marks on fabrication layer. Removing owned
        # child shapes corrupts this KiCad 10 SWIG binding's footprint proxy.
        for item in fp.GraphicalItems(): item.SetLayer(k.F_Fab)
        # Bounds measured from the corresponding assembly in ORCATemplate.step.
        half = 15.16 if count==20 else 8.81
        rect(fp,-9.7,-half-.3,3.75,half+.3,k.F_CrtYd)
        rect(fp,-9.43,-half,3.47,half,k.F_Fab,.1)
        for pad in fp.Pads(): pad.SetNetCode(0)
        # The source incorrectly tagged these PTH connectors as SMD.
        fp.SetAttributes(k.FP_THROUGH_HOLE)
        name = f'ORCA_{count}_RA'
        model_path = ROOT/'models'/f'{name}.step'
        if model_path.exists():
            model = k.FP_3DMODEL(); model.m_Filename='${KIPRJMOD}/models/'+model_path.name
            fp.Add3DModel(model)
        save_lib(fp,'GPIOJoiner',name)
    switch = k.FootprintLoad(str(LIBS/'Button_Switch_THT.pretty'),'SW_CK_JS202011CQN_DPDT_Straight')
    for pad in switch.Pads():
        if pad.GetNumber()=='4': pad.SetNumber('6')
        elif pad.GetNumber()=='6': pad.SetNumber('4')
    localize_models(switch)
    save_lib(switch,'GPIOJoiner','SW_JS202011CQN')
    used = {
        'Package_TO_SOT_SMD':['SOT-23','SOT-23-5'],
        'Resistor_SMD':['R_0603_1608Metric'],
        'Capacitor_SMD':['C_0603_1608Metric'],
        'TestPoint':['TestPoint_Pad_D1.5mm'],
        'MountingHole':['MountingHole_3.2mm_M3'],
    }
    for lib,names in used.items():
        for name in names:
            fp = k.FootprintLoad(str(LIBS/(lib+'.pretty')),name)
            localize_models(fp); save_lib(fp,lib,name)
    entries = '\n'.join(f'  (lib (name "{lib}") (type "KiCad") (uri "${{KIPRJMOD}}/{lib}.pretty") (options "") (descr "Project-local verified footprints"))'
                        for lib in ['GPIOJoiner',*used])
    (ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7)\n'+entries+'\n)\n',encoding='utf-8')


def make_project():
    default = dict(name='Default',clearance=.15,track_width=.2,via_diameter=.8,via_drill=.4,
                   diff_pair_width=.3,diff_pair_gap=.25,diff_pair_via_gap=.25,
                   microvia_diameter=.3,microvia_drill=.1,bus_width=12,wire_width=6,
                   line_style=0,priority=2147483647)
    project = {
        'meta':{'filename':'gpiojoiner.kicad_pro','version':1},
        'board':{'design_settings':{'meta':{'version':2},'rules':{
            'min_clearance':.15,'min_track_width':.2,'min_copper_edge_clearance':.3,
            'min_through_hole_diameter':.3,'min_via_diameter':.6,'min_via_annular_width':.1,
            'min_hole_clearance':.25,'min_hole_to_hole':.25,
            'min_silk_clearance':.15,'min_text_height':1.0,'min_text_thickness':.15,
            'min_resolved_spokes':2}, 'defaults':{'board_outline_line_width':.05}}},
        'net_settings':{'meta':{'version':5},'classes':[default],'netclass_patterns':[]},
        'text_variables':{'REVISION':'A - REVIEW PROTOTYPE'},
        'schematic':{'legacy_lib_dir':'','legacy_lib_list':[]},
    }
    (ROOT/'gpiojoiner.kicad_pro').write_text(json.dumps(project,indent=2)+'\n',encoding='utf-8')


def silk(board,text,x,y,size=1.3,angle=0,layer=k.F_SilkS):
    size=max(size,1.0)
    item = k.PCB_TEXT(board); item.SetText(text); item.SetPosition(v(x,y));item.SetLayer(layer)
    item.SetTextSize(v(size,size));item.SetTextThickness(k.FromMM(.18 if size>=1.3 else .15))
    item.SetTextAngle(k.EDA_ANGLE(angle,k.DEGREES_T))
    if layer==k.B_SilkS: item.SetMirrored(True)
    board.Add(item)


def build():
    xml = ET.parse(ROOT/'reports/netlist.xml').getroot()
    schematic = (ROOT/'gpiojoiner.kicad_sch').read_text(encoding='utf-8')
    root_uuid = re.search(r'\(uuid "([^"]+)"\)',schematic).group(1)
    board=k.BOARD();board.SetFileName(str(ROOT/'gpiojoiner.kicad_pcb'))
    ds=board.GetDesignSettings();ds.SetCopperLayerCount(2);ds.SetBoardThickness(k.FromMM(1.6))
    ds.SetAuxOrigin(v(85,215))
    ds.m_CopperEdgeClearance=k.FromMM(.3);ds.m_MinClearance=k.FromMM(.15)
    ds.m_TrackMinWidth=k.FromMM(.2);ds.m_ViasMinSize=k.FromMM(.6)
    nc=ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(k.FromMM(.15));nc.SetTrackWidth(k.FromMM(.2))
    nc.SetViaDiameter(k.FromMM(.8));nc.SetViaDrill(k.FromMM(.4))
    nets={};pin_net={}
    for n in xml.findall('./nets/net'):
        net=k.NETINFO_ITEM(board,n.get('name'));board.Add(net);nets[n.get('name')]=net
        for node in n.findall('node'):pin_net[node.get('ref'),node.get('pin')]=net
    for a,b in zip(OUTLINE,OUTLINE[1:]+OUTLINE[:1]):line(board,a,b,k.Edge_Cuts,.05)
    for comp in xml.findall('./components/comp'):
        ref=comp.get('ref');lib,name=comp.findtext('footprint').split(':')
        fp=k.FootprintLoad(str(ROOT/(lib+'.pretty')),name)
        if fp is None:raise FileNotFoundError(comp.findtext('footprint'))
        board.Add(fp);fp.SetReference(ref);fp.SetValue(comp.findtext('value'))
        fp.SetFPIDAsString(comp.findtext('footprint'));fp.SetUuid(uid('fp',ref))
        for field in comp.findall('./fields/field'):
            if field.get('name') not in ['Footprint','Reference','Value']:
                fp.SetField(field.get('name'),field.text or '')
                fp.GetField(field.get('name')).SetVisible(False)
        path=k.KIID_PATH();path.push_back(k.KIID(root_uuid));path.push_back(k.KIID(comp.findtext('tstamps').split()[0]));fp.SetPath(path)
        for i,pad in enumerate(fp.Pads()):
            pad.SetUuid(uid('pad',ref,i))
            if (ref,pad.GetNumber()) in pin_net:pad.SetNet(pin_net[ref,pad.GetNumber()])
        for i,item in enumerate(fp.GraphicalItems()):item.SetUuid(uid('shape',ref,i))
        fp.Reference().SetUuid(uid('reference',ref));fp.Value().SetUuid(uid('value',ref))
        x,y,angle=PLACEMENT[ref];fp.SetOrientationDegrees(angle);fp.SetPosition(v(x,y))
        fp.Value().SetVisible(False);fp.Reference().SetTextSize(v(1,1));fp.Reference().SetTextThickness(k.FromMM(.15))
        fp.Reference().SetTextAngle(k.EDA_ANGLE(0,k.DEGREES_T))
        if ref.startswith('J'):
            fp.Reference().SetVisible(False)
            pad1=next(p for p in fp.Pads() if p.GetNumber()=='1');p=pad1.GetPosition()
            px,py=k.ToMM(p.x),k.ToMM(p.y)
            dx,dy={0:(5.2,0),180:(-5.2,0),270:(0,5.2),90:(0,-5.2)}[angle]
            silk(board,'1',px+dx,py+dy,1)
        else:
            fp.Reference().SetPosition(v(x,y-2.4))
        if ref in ['R5','R6','R7','R8']:fp.SetDNP(True)
    for i,(x,y) in enumerate([(118,118),(182,118),(182,182),(118,182)],1):
        fp=k.FootprintLoad(str(ROOT/'MountingHole.pretty'),'MountingHole_3.2mm_M3')
        board.Add(fp);fp.SetReference(f'H{i}');fp.SetPosition(v(x,y));fp.SetUuid(uid('hole',i))
        fp.SetFPIDAsString('MountingHole:MountingHole_3.2mm_M3')
        fp.SetAttributes(k.FP_BOARD_ONLY|k.FP_EXCLUDE_FROM_BOM|k.FP_EXCLUDE_FROM_POS_FILES)
        fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
    silk(board,'GPIO JOINER',150,127,3)
    silk(board,'ORCA  /  REV A',150,133,1.5)
    silk(board,'TWO DEVICES ONLY',150,139,1.5)
    silk(board,'ONE DEVICE PER SIDE',150,142,1.2)
    silk(board,'SIDE A  /  FW2',101,148,1.6,90)
    silk(board,'SIDE B  /  FW2',199,152,1.6,90)
    silk(board,'SIDE A  /  OG',150,99,1.8)
    silk(board,'SIDE B  /  OG',150,201,1.8)
    silk(board,'J1:20',107,139.82,1,90);silk(board,'J2:10',107,166.54,1,90)
    silk(board,'J3:20',193,160.18,1,90);silk(board,'J4:10',193,133.46,1,90)
    silk(board,'J5',169,91,1);silk(board,'J6',131,209,1)
    silk(board,'VREF MODE',150,154,1.2)
    silk(board,'FW2 / MIXED',135,149,1)
    silk(board,'OG / OG',165,149,1)
    silk(board,'CHANGE WITH POWER OFF',150,158,1)
    silk(board,'ORCA ID',150,180,1.2)
    silk(board,'AIN2 = opposite VOUT / 2',150,187,1.1)
    silk(board,'REVIEW PROTOTYPE',150,193,1.1)
    for text,x,y in [('GPIO25 A',121,153),('GPIO25 B',179,153),('AIN3 A',99,180),('AIN3 B',201,116),
                     ('ID VCC',139,176),('GND',159,175),('120R DNP',98,135),('120R DNP',202,165)]:
        silk(board,text,x,y,.9)
    silk(board,'PAIR ONE SIDE A WITH ONE SIDE B',150,140,1.4,layer=k.B_SilkS)
    silk(board,'FW2 / MIXED: ONE FW2 SOURCES VREF\nOG / OG: EACH OG USES ITS OWN 3V3\nPROG VOUT READBACK: 2 x AIN2',150,157,1.1,layer=k.B_SilkS)
    silk(board,'Shared I2C1 ID: 24LC02BT\nGPIO JOINER REV A - 2026-09-08',150,165,1.2,layer=k.B_SilkS)
    for layer in [k.F_Cu,k.B_Cu]:
        zone=k.ZONE(board);zone.SetLayer(layer);zone.SetNet(nets['GND']);zone.SetLocalClearance(k.FromMM(.25))
        zone.SetPadConnection(k.ZONE_CONNECTION_THERMAL);zone.SetThermalReliefGap(k.FromMM(.25));zone.SetThermalReliefSpokeWidth(k.FromMM(.3))
        zone.SetMinThickness(k.FromMM(.2));zone.Outline().NewOutline()
        for x,y in OUTLINE:zone.Outline().Append(int(k.FromMM(x)),int(k.FromMM(y)))
        board.Add(zone)
    board.BuildListOfNets();board.SynchronizeNetsAndNetClasses(False)
    k.SaveBoard(str(ROOT/'gpiojoiner.kicad_pcb'),board)
    print(f'Generated PCB: {len(list(board.GetFootprints()))} footprints, {len(nets)} nets, 130 x 130 mm cross')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rebuild',action='store_true',required=True)
    ap.add_argument('--reference',type=Path,default=Path(tempfile.gettempdir())/'gpiojoiner-fw2-orca-templates/kicad/ORCATemplate.kicad_pcb')
    args=ap.parse_args()
    make_project();make_libraries(args.reference);build()
