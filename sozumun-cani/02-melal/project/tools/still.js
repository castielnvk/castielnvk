const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{ const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1080,height:1920}});
 const errs=[]; pg.on('pageerror',e=>errs.push(e.message)); pg.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await pg.goto('file://'+process.argv[2]+'/index.html'); await pg.evaluate(()=>document.fonts.ready); await pg.evaluate(()=>window.LOGO_READY);
 await pg.evaluate(async()=>{for(const f of ['400 20px PF','600 20px PF','italic 400 20px PF','400 20px LO','italic 400 20px LO','400 20px Inter','600 20px Inter']) await document.fonts.load(f,'əİöüşçğı');});
 const ts=process.argv[3].split(',').map(Number); fs.mkdirSync(process.argv[4],{recursive:true});
 for(const t of ts){ const d=await pg.evaluate(t=>frameJPEG(t,Math.round(t*30)),t); fs.writeFileSync(`${process.argv[4]}/t${t.toFixed(2)}.png`,Buffer.from(d.split(',')[1],'base64')); }
 if(errs.length) console.log('ERR',errs.slice(0,5)); await b.close(); })();
