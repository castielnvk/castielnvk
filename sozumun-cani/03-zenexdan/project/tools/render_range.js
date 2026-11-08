const { chromium } = require('playwright'); const { spawn } = require('child_process');
const FPS=30, proj=process.argv[2], out=process.argv[3], a0=+process.argv[4], a1=+process.argv[5], K=4;
(async()=>{ const b=await chromium.launch(); await Promise.all([...Array(K).keys()].map(async k=>{
 const s=a0+Math.floor((a1-a0)*k/K), e=a0+Math.floor((a1-a0)*(k+1)/K);
 const pg=await b.newPage({viewport:{width:1080,height:1920}}); await pg.goto('file://'+proj+'/index.html');
 await pg.evaluate(async()=>{await document.fonts.ready; await window.LOGO_READY; for(const f of ['400 20px FR','600 20px FR','italic 300 20px FR','italic 400 20px FR','400 20px Inter','500 20px Inter','600 20px Inter']) await document.fonts.load(f,'əİöüşçğı');});
 const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',''+FPS,'-c:v','png','-i','-','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-r',''+FPS,`${out}/r${k}.mp4`],{stdio:['pipe','inherit','inherit']});
 for(let i=s;i<e;i++){ const d=await pg.evaluate(([t,f])=>frameJPEG(t,f),[i/FPS,i]); if(!ff.stdin.write(Buffer.from(d.slice(22),'base64'))) await new Promise(r=>ff.stdin.once('drain',r)); }
 ff.stdin.end(); await new Promise(r=>ff.on('close',r)); })); await b.close(); console.log('done'); })();
