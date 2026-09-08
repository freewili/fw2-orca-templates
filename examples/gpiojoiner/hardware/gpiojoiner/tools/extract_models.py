"""Extract the two real docking connector shapes from ORCATemplate.step.

Optional regeneration helper; requires cadquery-ocp. The shipped local STEP
files do not need Python or OCP to view in KiCad. The source assembly is the
upstream template referenced in DESIGN.md, not a complete FreeWili enclosure.
"""
from pathlib import Path
import argparse
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.collections import Sequence_TDF_Label
from OCP.gp import gp_Trsf, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.IFSelect import IFSelect_RetDone


def extract(source):
    reader=STEPCAFControl_Reader();reader.SetNameMode(True)
    document=TDocStd_Document(TCollection_ExtendedString('ORCA'))
    assert reader.ReadFile(str(source))==IFSelect_RetDone
    assert reader.Transfer(document)
    shape_tool=XCAFDoc_DocumentTool.ShapeTool_s(document.Main())
    roots=Sequence_TDF_Label();shape_tool.GetFreeShapes(roots)
    assert roots.Length()==1,'Unexpected STEP top-level assembly'
    parts=Sequence_TDF_Label();shape_tool.GetComponents_s(roots.Value(1),parts)
    assert parts.Length()==3,'Expected two connectors plus template PCB'
    output=Path(__file__).resolve().parents[1]/'models';output.mkdir(exist_ok=True)
    for index,count,y in [(1,20,97.32),(2,10,124.04)]:
        transform=gp_Trsf();transform.SetTranslation(gp_Vec(-135.44,y,-1.51))
        shape=BRepBuilderAPI_Transform(shape_tool.GetShape_s(parts.Value(index)),transform,True).Shape()
        writer=STEPControl_Writer();assert writer.Transfer(shape,STEPControl_AsIs)==IFSelect_RetDone
        dest=output/f'ORCA_{count}_RA.step';assert writer.Write(str(dest))==IFSelect_RetDone
        print(dest.name,dest.stat().st_size,'bytes')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path)
    extract(ap.parse_args().source)
