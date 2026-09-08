"""Apply the documented local finishing edits to the rev A router output.

Run with KiCad Python after route_pcb.py. Coordinates identify the reviewed
router junctions; all incident segment ends move together. Run DRC afterward.
This helper is specific to the delivered routing, not a general DRC fixer.
"""
from pathlib import Path
import pcbnew as k

ROOT=Path(__file__).resolve().parents[1]


def finish():
    path=ROOT/'gpiojoiner.kicad_pcb';board=k.LoadBoard(str(path))
    moves={
        ('GND',182.3452,110.1852):(182.3452,110.7),
        ('GND',195.0752,110.1852):(195.0752,110.7),
        ('SPI_CS',114.4913,214.5869):(114.4913,214.1),
        ('UART_B_TX_A_RX',149.938,214.602):(149.938,214.55),
        ('UART_B_TX_A_RX',148.2074,214.602):(148.2074,214.55),
    }
    changed=0
    for track in board.GetTracks():
        for getter,setter in [(track.GetStart,track.SetStart),(track.GetEnd,track.SetEnd)]:
            p=getter();key=(track.GetNetname(),round(k.ToMM(p.x),4),round(k.ToMM(p.y),4))
            if key in moves:
                x,y=moves[key];setter(k.VECTOR2I(k.FromMM(x),k.FromMM(y)));changed+=1
    # Preserve the long edge-parallel trace when its via moves inward. Bend
    # only beside the via, away from the outer row of connector pads.
    for track in list(board.GetTracks()):
        start,end=k.VECTOR2I(track.GetStart()),k.VECTOR2I(track.GetEnd())
        if (track.GetNetname()=='SPI_CS' and track.GetLayer()==k.F_Cu
                and start==k.VECTOR2I(k.FromMM(160.1131),k.FromMM(214.5869))
                and end==k.VECTOR2I(k.FromMM(114.4913),k.FromMM(214.1))):
            bend=k.VECTOR2I(k.FromMM(114.9782),k.FromMM(214.5869))
            track.SetEnd(bend)
            jog=k.PCB_TRACK(board);jog.SetStart(bend);jog.SetEnd(end)
            jog.SetWidth(track.GetWidth());jog.SetLayer(track.GetLayer())
            jog.SetNetCode(track.GetNetCode());board.Add(jog)
    # A smaller thermal gap gives this edge ground pad room for its spokes.
    for fp in board.GetFootprints():
        if fp.GetReference()=='J3':
            pad=next(p for p in fp.Pads() if p.GetNumber()=='19')
            pad.SetThermalGap(k.FromMM(.15))
    # Put each connector reference at its actual connector center; a rotated
    # combined string reverses the apparent top/bottom ordering.
    from generate_pcb import silk, v
    for text in list(board.GetDrawings()):
        if type(text)!=k.PCB_TEXT: continue
        if text.GetText()=='J1:20     J2:10':
            text.SetText('J1:20');text.SetPosition(v(107,139.82))
            silk(board,'J2:10',107,166.54,1,90)
        elif text.GetText()=='J4:10     J3:20':
            text.SetText('J3:20');text.SetPosition(v(193,160.18))
            silk(board,'J4:10',193,133.46,1,90)
    k.ZONE_FILLER(board).Fill(board.Zones());k.SaveBoard(str(path),board)
    print('Applied local edge/ground finishing edits;',changed,'track endpoints moved')


if __name__=='__main__': finish()
