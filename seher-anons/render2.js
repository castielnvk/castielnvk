const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const s=process.argv[2],N=+process.argv[3],fps=24;const only=process.argv[4]?process.argv[4].split(',').map(Number):null;
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto(`file://${process.cwd()}/anons.html?p=${s}`);await p.evaluate(()=>document.fonts.ready);
fs.mkdirSync(`out/N${s}`,{recursive:true});
for(const i of (only||[...Array(N).keys()].map(x=>x+1))){await p.evaluate(([t,i])=>setT(t,i),[(i-1)/fps,i]);if(i<3)await p.evaluate(()=>document.fonts.ready);
await p.screenshot({path:`out/N${s}/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:96});}
await b.close()})();
