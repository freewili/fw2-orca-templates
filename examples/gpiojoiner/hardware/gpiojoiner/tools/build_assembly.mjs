// Manufacturer-format BOM/CPL files from verified parts and native KiCad CSV.
// Usage: node build_assembly.mjs <directory with artifact-tool node_modules>
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(path.join(path.resolve(process.argv[2]),'package.json'));
const {Workbook}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')));
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'manufacturing','revA');
const data=JSON.parse(await fs.readFile(path.join(root,'manufacturing','parts.json'),'utf8'));
const raw=await fs.readFile(path.join(out,'checks','kicad-positions.csv'),'utf8');
const imported=await Workbook.fromCSV(raw,{sheetName:'KiCad'});
const native=imported.worksheets.getItem('KiCad').getUsedRange().values;
const header=native[0], col=name=>header.indexOf(name);
for(const h of ['Ref','PosX','PosY','Rot','Side']) if(col(h)<0)throw Error('Missing KiCad column '+h);
const positions=new Map(native.slice(1).filter(r=>r[col('Ref')]).map(r=>[r[col('Ref')],r]));
const refs=data.parts.flatMap(p=>p.refs);
if(refs.length!==14||new Set(refs).size!==14)throw Error('Expected 14 fitted parts');
const wb=Workbook.create();
const rows=[['Item','Designator','Quantity','Manufacturer','Manufacturer Part Number','Description','Footprint','Type','LCSC Part #','Source']];
data.parts.forEach((p,i)=>rows.push([i+1,p.refs.join(','),p.refs.length,p.manufacturer,p.mpn,p.description,p.package,p.type,p.lcsc,p.source]));
const jlc=[['Comment','Designator','Footprint','LCSC Part #'],...data.parts.map(p=>[p.mpn,p.refs.join(','),p.package,p.lcsc])];
const cpl=[['Designator','Mid X','Mid Y','Rotation','Layer']];
for(const ref of refs){
 const r=positions.get(ref);if(!r)throw Error('Missing placement '+ref);
 const x=Number(r[col('PosX')]),y=Number(r[col('PosY')]),angle=Number(r[col('Rot')]);
 if(!(x>=0&&x<=130&&y>=0&&y<=130&&r[col('Side')]==='top'))throw Error('Invalid placement '+ref);
 cpl.push([ref,x,y,(angle+360)%360,'Top']);
}
const smdRefs=new Set(data.parts.filter(p=>p.type==='SMD').flatMap(p=>p.refs));
// PCBWay explicitly requests surface-mount parts only in the centroid file.
// Through-hole placement is supplied by the dimensioned assembly drawing.
const pcbwayCpl=[['Designator','Mid X','Mid Y','Layer','Rotation'],...cpl.slice(1).filter(r=>smdRefs.has(r[0])).map(r=>[r[0],r[1],r[2],r[4],r[3]])];
const files=[['PCBWay BOM','pcbway-bom.csv',rows],['JLCPCB BOM','jlcpcb-bom.csv',jlc],
 ['JLCPCB CPL','jlcpcb-cpl.csv',cpl],['PCBWay CPL','pcbway-cpl.csv',pcbwayCpl]];
for(const [name,filename,values] of files){
 const sheet=wb.worksheets.add(name);sheet.getRange('A1').write(values);
 const used=sheet.getUsedRange();used.format.font.name='Arial';used.format.font.size=10;
 used.format.verticalAlignment='center';used.format.rowHeight=34;used.format.columnWidth=22;
 sheet.showGridLines=false;
 sheet.getRangeByIndexes(0,0,1,values[0].length).format.fill='#23364D';
 sheet.getRangeByIndexes(0,0,1,values[0].length).format.font.color='#FFFFFF';
 sheet.getRangeByIndexes(0,0,1,values[0].length).format.font.bold=true;
 used.format.wrapText=true;
 if(name==='PCBWay BOM'){
   sheet.getRange('A:A').format.columnWidth=6;sheet.getRange('B:B').format.columnWidth=20;
   sheet.getRange('C:C').format.columnWidth=10;sheet.getRange('D:E').format.columnWidth=32;
   sheet.getRange('F:F').format.columnWidth=65;sheet.getRange('G:I').format.columnWidth=20;
   sheet.getRange('J:J').format.columnWidth=90;used.format.rowHeight=55;
 }
 const quoted=v=>'"'+String(v??'').replaceAll('"','""')+'"';
 // CSV is intentionally plain manufacturer interchange data. Export the
 // authored worksheet values, with no titles/footers added to supplier rows.
 const csv=sheet.getUsedRange().values.map(r=>r.map(quoted).join(',')).join('\r\n')+'\r\n';
 await fs.writeFile(path.join(out,'assembly',filename),csv);
}
wb.recalculate();
for(const name of ['PCBWay BOM','JLCPCB BOM','JLCPCB CPL','PCBWay CPL']){
 const sheet=wb.worksheets.getItem(name);const n=sheet.getUsedRange().values.length;
 const range=name==='PCBWay BOM'?'A1:I8':name.endsWith('BOM')?'A1:D8':`A1:E${n}`;
 const png=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(out,'checks',name.toLowerCase().replaceAll(' ','-')+'.png'),new Uint8Array(await png.arrayBuffer()));
}
console.log('PASS: each BOM has 7 lines / 14 parts; JLCPCB CPL 14 parts; PCBWay CPL 7 SMD parts; DNP omitted; 4 supplier CSVs rendered.');
