// Rasterize independent Gerbonara previews with SVG filter support.
// Usage: node render_cam.mjs <directory with sharp node_modules>
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const require=createRequire(path.join(path.resolve(process.argv[2]),'package.json'));
const sharp=require('sharp');
const out=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../manufacturing/revA/checks');
for(const side of ['top','bottom']){
 await sharp(path.join(out,`gerber-${side}.svg`),{density:300})
  .resize(1600,1600).png().toFile(path.join(out,`gerber-${side}.png`));
}
console.log('Rendered independent top and bottom Gerber previews.');
