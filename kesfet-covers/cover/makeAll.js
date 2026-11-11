// usage: node makeAll.js [n ...]  renders covers for jobs.json (all, or only listed numbers) into out/
const { chromium } = require('playwright'); const fs=require('fs'),path=require('path');
const jobs=JSON.parse(fs.readFileSync(path.join(__dirname,'../pipeline/jobs.json'),'utf8'));
const only=process.argv.slice(2).map(Number); fs.mkdirSync(path.join(__dirname,'out'),{recursive:true});
const tpl=fs.readFileSync(path.join(__dirname,'A_tpl.html'),'utf8');
const slug=s=>s.normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/ə/gi,'e').replace(/ı/g,'i').replace(/[^A-Za-z0-9]+/g,'_').replace(/^_|_$/g,'');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const j of jobs){ if(only.length&&!only.includes(j.n)) continue;
  const pick=(f)=>fs.existsSync(path.join(__dirname,'subjects_v2',f))?`subjects_v2/${f}`:`subjects/${f}`;
  const sub=pick(`${j.id}.png`); if(!fs.existsSync(path.join(__dirname,sub))){console.log(j.n,'no subject yet');continue}
  const cfg={subject:sub,w1:j.w1,w2:j.w2,w3:j.w3,tag:j.tag,lead:j.lead,name:j.name,palette:j.pal,sw:j.sw,dy:j.dy,noglow:j.n===42};
  for(const [k,suf] of [['subjL','_l'],['subjR','_r']]) if(j.multi&&(fs.existsSync(path.join(__dirname,`subjects/${j.id}${suf}.png`))||fs.existsSync(path.join(__dirname,`subjects_v2/${j.id}${suf}.png`)))) cfg[k]=pick(`${j.id}${suf}.png`);
  fs.writeFileSync(path.join(__dirname,'_a.html'),tpl.replace('<script>','<script>window.CFG='+JSON.stringify(cfg)+';'));
  await p.goto('file://'+path.join(__dirname,'_a.html'));await p.evaluate(()=>document.fonts.ready);
  await p.evaluate(()=>{document.querySelectorAll('.fit').forEach(B=>{const max=+B.dataset.max||940;let fs=parseFloat(getComputedStyle(B).fontSize);while(B.getBoundingClientRect().width>max&&fs>30){fs-=2;B.style.fontSize=fs+'px'}});
    const last=document.getElementById('w3')||document.getElementById('w2');const r=last.getBoundingClientRect();
    const s=document.getElementById('subj'); s.style.top=(r.bottom-55+(window.CFG.dy||0))+'px';
    const L=document.getElementById('subjL'),R=document.getElementById('subjR'); const top=r.bottom+90;
    if(L){L.style.top=top+'px';L.style.left='-70px';} if(R){R.style.top=top+'px';R.style.right='-70px';}});
  if(j.edge||j.topfade) await p.evaluate((tf)=>{const s=document.getElementById('subj');if(window.CFG.noglow)s.style.filter='none';const v=(tf?'linear-gradient(180deg,transparent 0%,#000 6%,#000 72%,transparent 96%),':'linear-gradient(180deg,#000 72%,transparent 96%),')+'linear-gradient(90deg,transparent 0%,#000 4%,#000 96%,transparent 100%)';s.style.webkitMaskImage=v;},!!j.topfade);
  await p.evaluate(()=>Promise.all([...document.querySelectorAll('img')].map(i=>i.complete?1:new Promise(r=>{i.onload=r;i.onerror=r}))));
  const out=path.join(__dirname,'out',`${String(j.n).padStart(2,'0')}_${slug(j.name)}_${j.id}.png`);
  await p.screenshot({path:out}); console.log(j.n,'wrote',path.basename(out));}
await b.close()})();
