"""Create a dimensioned fit check and assembly reference PDF from exported CAD.

Run with Python containing reportlab. Dimensions are mm; page 1 is exactly 1:1.
"""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/revA'
G=json.loads((OUT/'checks/geometry.json').read_text())
PARTS=json.loads((ROOT/'manufacturing/parts.json').read_text())
FPS={f['ref']:f for f in G['footprints']}
BLUE=HexColor('#204A67');GRAY=HexColor('#64717E');RED=HexColor('#A83438')
STYLE=ParagraphStyle('body',fontName='Helvetica',fontSize=9,leading=12,textColor=black)


def para(c,text,x,y,width):
    p=Paragraph(text,STYLE);_,h=p.wrap(width,500);p.drawOn(c,x,y-h);return y-h


def heading(c,title,subtitle,page):
    c.setFillColor(BLUE);c.setFont('Helvetica-Bold',17);c.drawString(15*mm,263*mm,title)
    c.setFillColor(GRAY);c.setFont('Helvetica',9);c.drawString(15*mm,255*mm,subtitle)
    c.setStrokeColor(BLUE);c.setLineWidth(.7);c.line(15*mm,251*mm,201*mm,251*mm)
    c.setFont('Helvetica',8);c.drawString(15*mm,8*mm,'GPIO Joiner rev A | Prototype quotation / engineering review | 2026-09-08')
    c.drawRightString(201*mm,8*mm,f'{page} / 3')


def board(c,base=(43,82),scale=1,allparts=False):
    def xy(p):return ((base[0]+(p[0]-85)*scale)*mm,(base[1]+(215-p[1])*scale)*mm)
    c.setStrokeColor(black);c.setLineWidth(.15*mm)
    for a,b in G['outline']:c.line(*xy(a),*xy(b))
    for fp in G['footprints']:
        ref=fp['ref']
        if not allparts and not ref.startswith(('J','H')):continue
        for p in fp['pads']:
            x,y=xy(p['xy']);w,h=p['size'];dr=p['drill'][0]
            c.setStrokeColor(RED if fp['dnp'] else GRAY);c.setFillColor(white)
            if dr:
                c.circle(x,y,dr*mm*scale/2,stroke=1,fill=0)
                if ref.startswith('J'):c.circle(x,y,min(w,h)*mm*scale/2,stroke=1,fill=0)
            else:c.rect(x-w*mm*scale/2,y-h*mm*scale/2,w*mm*scale,h*mm*scale,stroke=1,fill=0)
            if p['number']=='1' and ref.startswith('J'):
                c.setFillColor(BLUE);c.setFont('Helvetica-Bold',7)
                dx,dy={'J1':(4,0),'J2':(4,0),'J3':(-5,0),'J4':(-5,0),'J5':(0,-4),'J6':(0,3)}[ref]
                c.drawString(x+dx*mm*scale,y+dy*mm*scale,'1')
        x,y=xy(fp['xy']);c.setFont('Helvetica-Bold',8);c.setFillColor(BLUE)
        if ref.startswith('J'):
            dx,dy={'J1':(12,0),'J2':(12,0),'J3':(-18,0),'J4':(-18,0),'J5':(0,-12),'J6':(0,12)}[ref]
            if allparts and ref=='J4':dx=-36
            c.drawString(x+dx*mm*scale,y+dy*mm*scale,f'{ref} / {len(fp["pads"])} pin')
        elif ref.startswith('H'):c.drawString(x+3*mm,y+3*mm,ref)
        elif allparts:
            callouts={'R1':(194,141),'R2':(206,145),'R3':(104,160),'R4':(93,160),
                      'D1':(141,159),'U1':(150,157),'C1':(160,160),
                      'R5':(138,178),'R6':(155,180),'TP6':(137,169),'TP5':(161,169)}
            if ref in callouts:
                tx,ty=xy(callouts[ref]);c.setStrokeColor(GRAY);c.setLineWidth(.3)
                c.line(x,y,tx,ty+(3.8 if ty<y else -1)*mm)
            else:tx,ty=x,y+2.7*mm
            c.setFillColor(RED if fp['dnp'] else BLUE)
            c.drawCentredString(tx,ty,ref+(' DNP' if fp['dnp'] else ''))
    return xy


def detail(c,ref,cx,cy,scale,netnames):
    fp=FPS[ref];mx=sum(p['xy'][0] for p in fp['pads'])/len(fp['pads']);my=sum(p['xy'][1] for p in fp['pads'])/len(fp['pads'])
    c.setFillColor(BLUE);c.setFont('Helvetica-Bold',12);c.drawCentredString(cx*mm,(cy+18)*mm,ref+' - TOP VIEW')
    for p in fp['pads']:
        x=(cx+(p['xy'][0]-mx)*scale)*mm;y=(cy-(p['xy'][1]-my)*scale)*mm
        w,h=p['size'];c.setStrokeColor(GRAY);c.setFillColor(HexColor('#E8EDF1'))
        c.rect(x-w*mm*scale/2,y-h*mm*scale/2,w*mm*scale,h*mm*scale,stroke=1,fill=1)
        c.setFillColor(black);c.setFont('Helvetica-Bold',9);c.drawCentredString(x,y-3,p['number'])
        if ref!='SW1':
            label=netnames[p['number']];c.setFont('Helvetica',8)
            if p['xy'][0]<mx:c.drawRightString(x-w*mm*scale/2-3,y-3,label)
            else:c.drawString(x+w*mm*scale/2+3,y-3,label)


def make():
    target=OUT/'drawings/gpiojoiner-revA-manufacturing.pdf'
    c=canvas.Canvas(str(target),pagesize=letter);c.setTitle('GPIO Joiner rev A - manufacturing and fit reference')
    heading(c,'Mechanical fit check - print at 100%','US Letter. Actual size / 1:1. Disable Fit to page. All dimensions in mm.',1)
    xy=board(c)
    c.setStrokeColor(BLUE);c.setFillColor(BLUE);c.setLineWidth(.4)
    c.line(43*mm,224*mm,173*mm,224*mm)
    for x in [43,173]:c.line(x*mm,221*mm,x*mm,227*mm)
    c.setFont('Helvetica-Bold',10);c.drawCentredString(108*mm,226*mm,'130.00')
    c.line(30*mm,82*mm,30*mm,212*mm)
    for y in [82,212]:c.line(27*mm,y*mm,33*mm,y*mm)
    c.saveState();c.translate(27*mm,147*mm);c.rotate(90);c.drawCentredString(0,0,'130.00');c.restoreState()
    for label,p in [('OG A / SIDE A',[150,109]),('FW2 A',[105,157]),('FW2 B',[195,148]),('OG B / SIDE B',[150,191])]:
        c.setFont('Helvetica-Bold',8);c.drawCentredString(*xy(p),label)
    para(c,'FW2 connector centers: <b>26.72 mm</b>. Pitch and row spacing: <b>2.54 mm</b>. Connector drill: <b>1.10 mm</b>. Four support holes: <b>3.20 mm NPTH</b>.',15*mm,68*mm,119*mm)
    para(c,'Compare this hole pattern with real FW2 and OG devices, using the actual keyed connectors. Verify pin 1, mating direction, enclosure clearance, and board thickness. Full device enclosures have not been validated.',15*mm,46*mm,119*mm)
    c.setStrokeColor(black);c.setFillColor(black);c.rect(146*mm,15*mm,50*mm,50*mm,fill=0)
    c.setFont('Helvetica-Bold',9);c.drawCentredString(171*mm,40*mm,'50 x 50 mm')
    c.setFont('Helvetica',8);c.drawCentredString(171*mm,35*mm,'Check BOTH axes')
    c.showPage()
    heading(c,'Assembly placement reference','Top view. All 14 fitted components on top. R5-R8 are DO NOT POPULATE.',2)
    board(c,base=(43,106),allparts=True)
    y=91*mm
    for refs,text in [
        ('J1 J3 J5 J6','Sullins SFH11-PBPC-D10-RA-BK (20 positions)'),
        ('J2 J4','Sullins SFH11-PBPC-D05-RA-BK (10 positions)'),
        ('SW1','C&K JS202011CQN - contact-state check required'),
        ('U1 / D1','24LC02BT-E/OT / BAT54C,215 - orientation on page 3'),
        ('C1 / R1-R4','100 nF X7R 50 V / 10 kohm 0.1%, 0603'),
        ('R5-R8','DNP: no components and no stencil apertures'),
        ('TP1-TP6 / H1-H4','Copper test pads / mounting holes; no purchased parts')]:
        c.setFillColor(BLUE);c.setFont('Helvetica-Bold',9);c.drawString(15*mm,y,refs)
        c.setFillColor(black);c.setFont('Helvetica',9);c.drawString(55*mm,y,text);y-=7*mm
    para(c,'Install the small SMD parts before the through-hole connectors. Connectors mate outward and overhang the board. Let the assembler add tooling rails/fiducials and choose a fixture or hand-solder operation; confirm the panel drawing before production.',15*mm,35*mm,186*mm)
    c.showPage()
    heading(c,'Assembly details and fabrication notes','Pin numbers below are PCB pad numbers. Check package markings and supplier placement preview.',3)
    detail(c,'U1',60,218,5,{'1':'SCL','2':'GND','3':'SDA','4':'VCC','5':'WP / GND'})
    detail(c,'D1',153,218,5,{'1':'FW2 A 3V3','2':'FW2 B 3V3','3':'EEPROM VCC'})
    detail(c,'SW1',62,163,4,{})
    para(c,'<b>VREF slide switch</b><br/>Left: pads 1-2 and 4-5 connected (FW2 / MIXED).<br/>Right: pads 2-3 and 5-6 connected (OG / OG).<br/>Verify with a meter on the actual part before fitting the batch. Never switch with devices powered.',109*mm,180*mm,88*mm)
    y=133*mm
    notes=[
        '<b>Prototype quote:</b> five boards as a working quantity. FR-4, two layers, 1.60 mm finished thickness, 1 oz finished copper, green solder mask, white legend both sides, lead-free ENIG finish.',
        '<b>Outline and holes:</b> CNC-route the cross. 130 x 130 mm bounding box. No V-score or castellations. Finished holes: 158 plated, 4 non-plated. Allow normal inside router corner radii up to 1 mm. Electrical test required.',
        '<b>Assembly:</b> seven SMD parts and seven through-hole parts per board. Four resistor positions are DNP. Do not substitute connectors, switch, EEPROM package, or diode configuration without review. Keep 0.1% divider resistors.',
        '<b>Coordinates:</b> Gerber/drill/CPL origin is lower left of the board bounding box. X right, Y up, mm. CPL uses native KiCad footprint origins/rotations. Through-hole origins are placement datums, not necessarily plastic-body centers. Align vendor models using the actual hole/pad pattern and this drawing.',
        '<b>EEPROM:</b> fit U1 blank. No programming image or factory functional test is supplied. During bring-up, use one I2C1 controller, verified 3.3 V pull-ups and at most 400 kHz. A programmed ORCA ID remains a separate task.',
        '<b>Use:</b> one device per side, two total. Set VREF mode with power off. Programmable-output measurement is 2 x the opposite AIN2 value. Physical fit and bench operation remain unverified.'
    ]
    for note in notes:y=para(c,note,15*mm,y,186*mm)-4*mm
    assert y>16*mm, 'Notes overflow page'
    c.save();print('Created',target)


if __name__=='__main__':make()
