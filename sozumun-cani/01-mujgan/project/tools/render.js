const { chromium } = require('playwright'); const { spawn } = require('child_process');
const FPS=30, DUR=71.83, N=Math.ceil(DUR*FPS), K=4, proj=process.argv[2], out=process.argv[3];
async function worker(k,b){ const a0=Math.floor(N*k/K), a1=Math.floor(N*(k+1)/K);
 const pg=await b.newPage({viewport:{width:1080,height:1920}}); await pg.goto('file://'+proj+'/index.html');
 await pg.evaluate(async()=>{await document.fonts.ready; await window.LOGO_READY; for(const f of ['300 20px CG','500 20px CG','italic 300 20px CG','italic 500 20px CG','500 20px CSC']) await document.fonts.load(f,'əİöüşçğı');});
 const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',''+FPS,'-c:v','png','-i','-','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-profile:v','high','-r',''+FPS,`${out}/seg${k}.mp4`],{stdio:['pipe','inherit','inherit']});
 for(let i=a0;i<a1;i++){ const d=await pg.evaluate(([t,f])=>frameJPEG(t,f),[i/FPS,i]); const buf=Buffer.from(d.slice(22),'base64'); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); if(i%150==0) console.log('w'+k,i,'/',a1); }
 ff.stdin.end(); await new Promise(r=>ff.on('close',r)); }
(async()=>{ const b=await chromium.launch(); await Promise.all([...Array(K).keys()].map(k=>worker(k,b))); await b.close(); console.log('done'); })();
