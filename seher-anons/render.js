const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const s=process.argv[2];const only=process.argv[3]?process.argv[3].split(',').map(Number):null;
const n=fs.readdirSync(`fr/${s}`).length;const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto(`file://${process.cwd()}/comic.html?s=${s}`);await p.evaluate(()=>document.fonts.ready);
fs.mkdirSync(`out/${s}`,{recursive:true});
for(const i of (only||[...Array(n).keys()].map(x=>x+1))){await p.evaluate(([t,i])=>setT(t,i),[(i-1)/25,i]);await p.evaluate(()=>document.fonts.ready);
await p.screenshot({path:`out/${s}/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:96});}
await b.close()})();
