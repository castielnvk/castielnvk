const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{ const b=await chromium.launch(); 
 for (const [dir,out] of (process.argv[5]?[[process.argv[2],process.argv[5]]]:[[process.argv[2],'Mujgan'],[process.argv[3],'Melal']])) {
  const pg=await b.newPage({viewport:{width:1080,height:1920}}); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+dir+'/index.html'); await pg.evaluate(async()=>{await document.fonts.ready; await window.LOGO_READY;
   for(const f of ['300 20px CG','500 20px CG','italic 300 20px CG','500 20px CSC','600 20px PF','italic 400 20px LO','500 20px Inter','600 20px FR','italic 300 20px FR']) { try{await document.fonts.load(f,'əİöüşçğı');}catch(e){} }});
  const d=await pg.evaluate(()=>{cover(); return document.getElementById('c').toDataURL('image/png');});
  fs.writeFileSync(`${process.argv[4]}/cover_${out}.png`,Buffer.from(d.split(',')[1],'base64')); if(errs.length) console.log(out,errs); }
 await b.close(); })();
