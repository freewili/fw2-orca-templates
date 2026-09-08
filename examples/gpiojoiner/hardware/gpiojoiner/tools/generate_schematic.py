"""Regenerate the review schematic; connectivity acceptance is in check_connections.py.

Python stdlib only. Symbols are embedded and copied into the project library.
Standard graphic symbols are taken from the installed KiCad 10 symbol library.
"""
from pathlib import Path
import re
import uuid
import os

ROOT=Path(__file__).resolve().parents[1]
SYMS=Path(os.environ.get('KICAD_SYMBOL_DIR',
    str(Path(os.environ.get('KICAD_INSTALL','C:/Program Files/KiCad/10.0'))/'share/kicad/symbols')))
NS=uuid.UUID('4bc1e7b4-eae5-4ddb-8b48-8e470103dc0a')
def uid(*v): return str(uuid.uuid5(NS,'/'.join(map(str,v))))
def q(s): return '"'+str(s).replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'
def f(n): return f'{n:.4f}'.rstrip('0').rstrip('.') if n else '0'
def fx(size=1.27,extra=''): return f'(effects (font (size {size} {size})) {extra})'
def prop(k,v,x=0,y=0,hidden=False,size=1.27):
    return f'(property {q(k)} {q(v)} (at {f(x)} {f(y)} 0) {fx(size,"(hide yes)" if hidden else "")})'
def pin(n,name,x,y,a=0,kind='passive',length=5.08):
    return f'(pin {kind} line (at {f(x)} {f(y)} {a}) (length {f(length)}) (name {q(name)} {fx(1.016)}) (number {q(n)} {fx(1.016)}))'
def rect(x1,y1,x2,y2):
    return f'(rectangle (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (stroke (width 0.254) (type default)) (fill (type background)))'
def poly(points,style='default'):
    return '(polyline (pts '+''.join(f'(xy {f(x)} {f(y)})' for x,y in points)+f') (stroke (width 0.254) (type {style})) (fill (type none)))'
def custom(name,ref,pins,graphics):
    return f'(symbol {q(name)} (pin_names (offset 0.635)) (in_bom yes) (on_board yes) '+prop('Reference',ref)+prop('Value',name)+f'(symbol {q(name+"_0_1")} {graphics}) (symbol {q(name+"_1_1")} '+''.join(pin(*p) for p in pins)+'))'
def extract(lib,name):
    s=(SYMS/(lib+'.kicad_sym')).read_text(encoding='utf-8')
    start=s.index('\t(symbol '+q(name)); depth=0; quoted=False; escape=False
    for j in range(start,len(s)):
        c=s[j]
        if escape: escape=False; continue
        if c=='\\' and quoted: escape=True; continue
        if c=='"': quoted=not quoted
        if not quoted:
            if c=='(': depth+=1
            elif c==')':
                depth-=1
                if not depth: return s[start:j+1].strip()
    raise ValueError(name)

libraries={}
coords={}
def add_custom(name,ref,pins,graphics):
    libraries[name]=custom(name,ref,pins,graphics)
    coords[name]={str(p[0]):(p[2],p[3],p[4] if len(p)>4 else 0) for p in pins}

signal20={1:'SPI_CS',2:'5V_OUT',3:'GPIO27',4:'VREF',5:'UART_RX',6:'3V3_OUT',7:'UART_CTS',8:'I2C0_SCL',9:'UART_TX',10:'I2C0_SDA',11:'UART_RTS',12:'SPI_RX',13:'SPI_TX',14:'GPIO26',15:'SPI_SCLK',16:'CAN_L',17:'GPIO25',18:'CAN_H',19:'GND',20:'GND'}
for name,og in [('FW2_20',False),('OG_20',True)]:
    signals=signal20.copy()
    if og: signals.update({16:'SWCLK',18:'SWDIO'})
    pins=[(p,signals[p],-22.86 if p%2 else 22.86,-((p-1)//2)*3.81,0 if p%2 else 180) for p in range(1,21)]
    add_custom(name,'J',pins,rect(-17.78,2.54,17.78,-36.83))
signals={1:'GND',2:'AIN3',3:'AOUT1',4:'AIN2',5:'AOUT0',6:'AIN1',7:'I2C1_SCL',8:'AIN0',9:'I2C1_SDA',10:'PROG_VOUT'}
add_custom('FW2_10','J',[(p,signals[p],-22.86 if p%2 else 22.86,-((p-1)//2)*3.81,0 if p%2 else 180) for p in range(1,11)],rect(-17.78,2.54,17.78,-17.78))
add_custom('24LC02BT','U',[(1,'SCL',-15.24,2.54,0,'input'),(3,'SDA',-15.24,-2.54,0,'bidirectional'),(5,'WP',15.24,-2.54,180,'input'),(4,'VCC',0,10.16,270,'power_in'),(2,'VSS',0,-10.16,90,'power_in')],rect(-10.16,5.08,10.16,-5.08))
# Custom one-unit switch: pin mapping follows the specific fitted JS202011CQN.
swpins=[(2,'',-7.62,5.08,0),(1,'',7.62,7.62,180),(3,'',7.62,2.54,180),(5,'',-7.62,-5.08,0),(4,'',7.62,-2.54,180),(6,'',7.62,-7.62,180)]
swgraphic=poly([(-2.54,5.08),(2.54,7.62)])+poly([(-2.54,-5.08),(2.54,-2.54)])+poly([(0,5.08),(0,-5.08)],'dash')
add_custom('JS202011CQN','SW',swpins,swgraphic)
add_custom('TestPoint','TP',[(1,'',0,0,90,'passive',2.54)],'(circle (center 0 3.175) (radius 0.635) (stroke (width 0.254) (type default)) (fill (type none)))')
for lib,name in [('Device','R'),('Device','C'),('Diode','BAT54C'),('power','PWR_FLAG')]: libraries[name]=extract(lib,name)
coords.update({'R':{'1':(0,3.81,270),'2':(0,-3.81,90)},'C':{'1':(0,3.81,270),'2':(0,-3.81,90)},'BAT54C':{'1':(-7.62,0,0),'2':(7.62,0,180),'3':(0,-5.08,90)},'PWR_FLAG':{'1':(0,0,90)}})

chunks=[]
instances={}
datasheets={
    '24LC02BT':'https://ww1.microchip.com/downloads/en/DeviceDoc/24AA02-24LC02B-24FC02-Data-Sheet-20001709L.pdf',
    'BAT54C':'https://assets.nexperia.com/documents/data-sheet/BAT54C.pdf',
    'JS202011CQN':'https://www.littelfuse.com/assetdocs/littelfuse-c-k-slide-js-series-datasheet?assetguid=aba42b08-0d2c-423b-813d-a2faa5a3bb14',
    'FW2_20':'https://docs.freewili.com/hardware/pinout/',
    'OG_20':'https://docs.freewili.com/hardware/pinout/',
    'FW2_10':'https://docs.freewili.com/hardware/pinout/',
}
def instance(name,ref,value,footprint,x,y,dnp=False,refpos=None,valpos=None):
    instances[ref]=(name,x,y)
    if refpos is None: refpos=(x,y-7.62)
    if valpos is None: valpos=(x,y-5.08)
    flags='no' if ref.startswith('#') else 'yes'
    bom='no' if ref.startswith(('#','TP')) else 'yes'
    fields=prop('Reference',ref,*refpos,hidden=ref.startswith('#'))+prop('Value',value,*valpos)
    fields+=prop('Footprint',footprint,x,y,True)+prop('Datasheet',datasheets.get(name,''),x,y,True)
    if dnp: fields+=prop('Assembly','DNP',x+8.89,y+2.54)
    chunks.append(f'(symbol (lib_id "GPIOJoiner:{name}") (at {f(x)} {f(y)} 0) (unit 1) (exclude_from_sim no) (in_bom {bom}) (on_board {flags}) (dnp {"yes" if dnp else "no"}) (uuid "{uid("symbol",ref)}") {fields} '+''.join(f'(pin "{p}" (uuid "{uid("pin",ref,p)}"))' for p in coords[name])+f'(instances (project "gpiojoiner" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
def xy(ref,p):
    name,x,y=instances[ref]; dx,dy,a=coords[name][str(p)]
    return x+dx,y-dy,a
def wire(x,y,xx,yy,key):
    chunks.append(f'(wire (pts (xy {f(x)} {f(y)}) (xy {f(xx)} {f(yy)})) (stroke (width 0) (type default)) (uuid "{uid("wire",key)}"))')
def label(net,x,y,angle=0,key=None):
    chunks.append(f'(global_label {q(net)} (shape passive) (at {f(x)} {f(y)} {angle}) {fx(1.016,"(justify "+("right" if angle==180 else "left")+")")} (uuid "{uid("label",key or (net,x,y))}") '+prop('Intersheetrefs','${INTERSHEET_REFS}',x,y,True)+')')
def connect(ref,p,net):
    x,y,a=xy(ref,p)
    if net is None:
        chunks.append(f'(no_connect (at {f(x)} {f(y)}) (uuid "{uid("nc",ref,p)}"))'); return
    if a==0: xx,yy,ang=x-5.08,y,180
    elif a==180: xx,yy,ang=x+5.08,y,0
    else: xx,yy,ang=x+7.62,y,0
    wire(x,y,xx,yy,(ref,p)); label(net,xx,yy,ang,key=(ref,p))
def note(s,x,y,size=1.27):
    chunks.append(f'(text {q(s)} (at {f(x)} {f(y)} 0) {fx(size,"(justify left top)")} (uuid "{uid("note",x,y)}"))')
def line(x,y,xx,yy):
    chunks.append(f'(polyline (pts (xy {f(x)} {f(y)})(xy {f(xx)} {f(yy)})) (stroke (width 0.254) (type default)) (uuid "{uid("line",x,y)}"))')

# Paired bus names refer to source/destination, making crossings readable.
maps={}
base={1:'SPI_CS',2:None,3:'GPIO_A27_B26',4:'VREF_A',5:'UART_B_TX_A_RX',6:'FW2_A_3V3',7:'UART_B_RTS_A_CTS',8:'I2C0_SCL',9:'UART_A_TX_B_RX',10:'I2C0_SDA',11:'UART_A_RTS_B_CTS',12:'SPI_B_TX_A_RX',13:'SPI_A_TX_B_RX',14:'GPIO_B27_A26',15:'SPI_SCLK',16:'CAN_L',17:'GPIO25_A',18:'CAN_H',19:'GND',20:'GND'}
maps['J1']=base.copy(); maps['J5']=base.copy(); maps['J5'].update({6:'OG_A_3V3',16:None,18:None})
swap={3:14,14:3,5:9,9:5,7:11,11:7,12:13,13:12}
maps['J3']={p:base[swap.get(p,p)] for p in base}; maps['J3'].update({4:'VREF_B',6:'FW2_B_3V3',17:'GPIO25_B'})
maps['J6']=maps['J3'].copy(); maps['J6'].update({6:'OG_B_3V3',16:None,18:None})
maps['J2']={1:'GND',2:'AIN3_A',3:'A_AOUT1_B_AIN1',4:'B_VOUT_HALF',5:'A_AOUT0_B_AIN0',6:'B_AOUT1_A_AIN1',7:'I2C1_SCL',8:'B_AOUT0_A_AIN0',9:'I2C1_SDA',10:'PROG_VOUT_A'}
maps['J4']={1:'GND',2:'AIN3_B',3:'B_AOUT1_A_AIN1',4:'A_VOUT_HALF',5:'B_AOUT0_A_AIN0',6:'A_AOUT1_B_AIN1',7:'I2C1_SCL',8:'A_AOUT0_B_AIN0',9:'I2C1_SDA',10:'PROG_VOUT_B'}
for ref,name,value,x,y,fp in [('J1','FW2_20','FW2 A - WEST',76.2,43.18,'ORCA_20_RA'),('J5','OG_20','OG A - NORTH',76.2,96.52,'ORCA_20_RA'),('J2','FW2_10','FW2 A - ANALOG / I2C1',76.2,149.86,'ORCA_10_RA'),('J3','FW2_20','FW2 B - EAST',208.28,43.18,'ORCA_20_RA'),('J6','OG_20','OG B - SOUTH',208.28,96.52,'ORCA_20_RA'),('J4','FW2_10','FW2 B - ANALOG / I2C1',208.28,149.86,'ORCA_10_RA')]:
    instance(name,ref,value,'GPIOJoiner:'+fp,x,y)
    for p,net in maps[ref].items(): connect(ref,p,net)

rfp='Resistor_SMD:R_0603_1608Metric'
def resistor(ref,value,x,y,n1,n2,dnp=False):
    instance('R',ref,value,rfp,x,y,dnp,refpos=(x-6.35,y-1.27),valpos=(x-8.89,y+1.27))
    connect(ref,1,n1); connect(ref,2,n2)
for upper,lower,y,source,mid in [('R1','R2',48.26,'PROG_VOUT_A','A_VOUT_HALF'),('R3','R4',88.9,'PROG_VOUT_B','B_VOUT_HALF')]:
    resistor(upper,'10k 0.1%',325.12,y,source,mid)
    instance('R',lower,'10k 0.1%',rfp,325.12,y+15.24,refpos=(318.77,y+13.97),valpos=(316.23,y+16.51))
    x1,y1,_=xy(upper,2); x2,y2,_=xy(lower,1)
    wire(x1,y1,x2,y2,(upper,lower))
    chunks.append(f'(junction (at {f(x1)} {f(y1)}) (diameter 0) (color 0 0 0 0) (uuid "{uid("junction",upper)}"))')
    connect(lower,2,'GND')
instance('JS202011CQN','SW1','JS202011CQN','GPIOJoiner:SW_JS202011CQN',335.28,146.05,refpos=(335.28,132.08),valpos=(335.28,134.62))
for p,n in {1:'VREF_LINK',2:'VREF_A',3:'OG_A_3V3',4:'VREF_LINK',5:'VREF_B',6:'OG_B_3V3'}.items(): connect('SW1',p,n)
instance('BAT54C','D1','BAT54C','Package_TO_SOT_SMD:SOT-23',76.2,207.01,refpos=(76.2,199.39),valpos=(76.2,201.93))
for p,n in {1:'FW2_A_3V3',2:'FW2_B_3V3',3:'EEPROM_VCC'}.items(): connect('D1',p,n)
instance('24LC02BT','U1','24LC02BT-E/OT','Package_TO_SOT_SMD:SOT-23-5',76.2,237.49,refpos=(76.2,222.25),valpos=(76.2,224.79))
for p,n in {1:'I2C1_SCL',2:'GND',3:'I2C1_SDA',4:'EEPROM_VCC',5:'GND'}.items(): connect('U1',p,n)
instance('C','C1','100nF','Capacitor_SMD:C_0603_1608Metric',132.08,234.95,refpos=(125.73,232.41),valpos=(125.73,237.49))
connect('C1',1,'EEPROM_VCC'); connect('C1',2,'GND')
resistor('R5','4.7k',187.96,203.2,'EEPROM_VCC','I2C1_SCL',True)
resistor('R6','4.7k',238.76,203.2,'EEPROM_VCC','I2C1_SDA',True)
resistor('R7','120',187.96,229.87,'CAN_L','CAN_H',True)
resistor('R8','120',238.76,229.87,'CAN_L','CAN_H',True)
for i,net in enumerate(['GPIO25_A','GPIO25_B','AIN3_A','AIN3_B','GND','EEPROM_VCC'],1):
    x=302.26 if i%2 else 358.14; y=203.2+((i-1)//2)*17.78
    instance('TestPoint','TP'+str(i),net,'TestPoint:TestPoint_Pad_D1.5mm',x,y,refpos=(x,y-7.62),valpos=(x,y-5.08))
    connect('TP'+str(i),1,net)
for i,net,x in [(1,'EEPROM_VCC',170.18),(2,'GND',231.14)]:
    instance('PWR_FLAG','#FLG'+str(i),'PWR_FLAG','',x,255.27,refpos=(x,251.46),valpos=(x,249.555)); connect('#FLG'+str(i),1,net)

note('GPIO JOINER / REV A / TWO-DEVICE TEST FIXTURE',15.24,12.7,2.54)
note('SIDE A: choose WEST FW2 or NORTH OG',20.32,25.4,1.524)
note('SIDE B: choose EAST FW2 or SOUTH OG',152.4,25.4,1.524)
note('DIVIDED PROGRAMMABLE OUTPUTS',292.1,25.4,1.524)
note('Firmware: VOUT = 2 x opposite AIN2\n0.1% divider; nominal range 0 to 2.75 V.',287.02,114.3)
note('ONE DEVICE PER SIDE / TWO DEVICES MAXIMUM',15.24,176.53,1.524)
note('Named nets implement SPI, UART and GPIO swaps. I2C0/I2C1 are direct.\n5 V outputs and OG SWD are intentionally not connected.',15.24,180.34)
note('ORCA IDENTIFICATION / SHARED I2C1',15.24,190.5,1.524)
note('OPTIONAL BUS COMPONENTS',162.56,190.5,1.524)
note('DNP pull-ups: measure host pull-ups first.',162.56,215.9)
note('DNP termination: check host termination.',162.56,241.3)
note('VREF MODE - SWITCH WITH POWER OFF',287.02,124.46,1.524)
note('FW2/mixed: contacts 1-2 and 4-5; linked VREF.\nEnable exactly ONE FW2 IO voltage source.\nOG/OG: contacts 2-3 and 5-6; local 3.3 V.',287.02,162.56)
note('SPARE SIGNALS / BENCH TEST POINTS',287.02,190.5,1.524)
note('U1 WP tied low for programming. EEPROM at 0x50.\nBAT54C isolates the two FW2 3.3 V outputs.\nEEPROM image and host power/pull-ups need bench validation.',15.24,256.54)
note('PROTOTYPE - VERIFY MATING AND FIRMWARE BEFORE FABRICATION',15.24,274.32,1.524)
line(279.4,25.4,279.4,262.89)
line(15.24,187.96,401.32,187.96)

libfile='(kicad_symbol_lib (version 20241209) (generator "gpiojoiner")\n'+'\n'.join(libraries.values())+'\n)\n'
(ROOT/'GPIOJoiner.kicad_sym').write_text(libfile,encoding='utf-8')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "GPIOJoiner")(type "KiCad")(uri "${KIPRJMOD}/GPIOJoiner.kicad_sym")(options "")(descr "Project-local verified GPIO joiner symbols")))\n',encoding='utf-8')
embedded='\n'.join(re.sub(r'^\(symbol "([^\"]+)"',r'(symbol "GPIOJoiner:\1"',s,count=1) for s in libraries.values())
sch=f'(kicad_sch (version 20260306) (generator "gpiojoiner") (uuid "{uid("root")}") (paper "A3") (title_block (title "GPIO Joiner - two-device GPIO test fixture") (date "2026-09-08") (rev "A")) (lib_symbols {embedded})\n'+ '\n'.join(chunks)+'\n(sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n'
(ROOT/'gpiojoiner.kicad_sch').write_text(sch,encoding='utf-8')
print(f'Generated schematic: {len(instances)} symbols, {len(sch)} bytes.')
