// Renders every SVG in _jobs.json to PNG with the pre-installed Chromium.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const jobs=JSON.parse(fs.readFileSync(path.join(__dirname,'_jobs.json')));
const b=await chromium.launch();const p=await b.newPage({deviceScaleFactor:1});
for(const j of jobs){fs.mkdirSync(path.dirname(j.png),{recursive:true});
 await p.setViewportSize({width:j.w,height:j.h});await p.goto('file://'+j.svg);
 await p.screenshot({path:j.png,omitBackground:j.transparent,clip:{x:0,y:0,width:j.w,height:j.h}});}
await b.close();console.log('rendered',jobs.length);})();
