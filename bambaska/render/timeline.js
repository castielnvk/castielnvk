// Timed lyrics for "Bambaşka biri".
// Word times come from faster-whisper (large-v3) on the Demucs vocal stem, mapped onto the
// lyrics the user supplied. Format: "word@time word@time ...".
// fx = special treatment key used by the renderer.
function L(sec, spec, opts = {}) {
  const words = spec.trim().split(/\s+/).map((tok) => {
    const i = tok.lastIndexOf('@');
    return { text: tok.slice(0, i).replace(/_/g, ' '), t: parseFloat(tok.slice(i + 1)) };
  });
  return { sec, words, t: words[0].t, ...opts };
}
// backing / echo line (rendered as cinematic italic subtitle)
function B(text, t0, t1) { return { text, t0, t1 }; }

const lines = [
  // ---- Verse 1
  L('v1', 'Yeter@10.0 ki@10.48 sen@10.72 iste@10.92', { fx: 'hearts' }),
  L('v1', 'Yaparım@11.44 her@12.84 şeyi@13.16', { fx: 'hearts' }),
  L('v1', 'Bilirsin@14.7 işte@15.36'),
  L('v1', 'Tek,@15.78 tek,@16.40 tek@16.80', { fx: 'tek' }),
  L('v1', 'zaafım@17.16 sendin@17.84', { fx: 'bigheart', accent: ['sendin'] }),
  L('v1', 'Kanadı@18.5 kırık@19.76 biri@20.08', { fx: 'wing', accent: ['kırık'] }),
  L('v1', 'Tamiri@20.64 yok@22.12 gibi@22.34', { fx: 'tape' }),
  L('v1', 'Kullandın@23.9 değil@24.7 mi?@24.88', { fx: 'puppet', accent: ['Kullandın'] }),
  L('v1', 'Esirin@25.86 oldum,@26.66 esirin..@27.28', { fx: 'cage', accent: ['esirin..'] }),
  // ---- Pre-chorus x2
  L('pre', 'Umursamazdın,@27.76 sorgulamazdım.@28.9', { fx: 'strike' }),
  L('pre', 'Tahminimden@30.0 çok@31.16 kurnazdın.@31.48', { fx: 'eye', accent: ['kurnazdın.'] }),
  L('pre', 'Sorun@32.36 sende@32.84 değil@33.3 dedin@33.52 ama@33.9 hep,@34.06', { fx: 'bubble' }),
  L('pre', 'Hep@34.42 suçlandım,@34.86 hep@35.8 suçlandım.@36.0', { fx: 'arrows', accent: ['suçlandım,', 'suçlandım.'] }),
  L('pre', 'Umursamazdın,@37.0 sorgulamazdım.@38.1', { fx: 'strike' }),
  L('pre', 'Tahminimden@39.3 çok@40.3 kurnazdın.@40.6', { fx: 'eye', accent: ['kurnazdın.'] }),
  L('pre', 'Sorun@41.5 sende@41.9 değil@42.5 dedin@42.7 ama@43.0 hep,@43.2', { fx: 'bubble' }),
  L('pre', 'Hep@43.6 suçlandım,@44.0 hep@45.0 suçlandım.@45.2', { fx: 'arrows', accent: ['suçlandım,', 'suçlandım.'] }),
  // ---- Chorus 1
  L('ch', 'Bambaşka@46.2 biri@47.4 oldum,@47.8 oldum.@50.0', { fx: 'split' }),
  L('ch', 'Bambaşka@51.0 biri@52.0 oldum.@52.5', { fx: 'split' }),
  L('ch', 'Bambaşka@55.7 biri@56.6', { fx: 'split' }),
  L('ch', 'Bambaşka@57.9 biri@58.8', { fx: 'split' }),
  L('ch', 'Bambaşka@60.0 biri@61.1 oldum,@61.5 oldum.@63.7', { fx: 'split' }),
  L('ch', 'Bambaşka@64.7 biri@65.7', { fx: 'split' }),
  L('ch', 'Bambaşka@66.4 biri@67.6', { fx: 'split' }),
  L('ch', 'Bambaşka@68.5 biri@70.2 oldum,@70.7 oldum.@72.8', { fx: 'split', end: 75.0 }),
  // ---- Verse 2
  L('v2', 'Nedir@75.7 seni@76.7 gece@76.9 bana@77.2 düşündüren?@77.5', { fx: 'moon', accent: ['gece'] }),
  L('v2', 'Yoksa@80.0 ben@81.0 miyim@81.2 yine@81.5 seni@81.7 düşünmek@82.0 için@82.6 geceyi@82.8 bekleyen?@83.2', { fx: 'moon', accent: ['geceyi'] }),
  L('v2', 'Kaybetme@84.5 korkusu@85.5 sardı,@86.1', { fx: 'vines' }),
  L('v2', 'Korkudan@86.8 öfke@87.9 klonlandı@88.2', { fx: 'clone', accent: ['öfke'] }),
  L('v2', 'Çoğaldı,@89.2 çoğaldı,@90.3', { fx: 'clone2' }),
  L('v2', 'ışığım@91.4 karanlığa@92.3 daldı.@93.1', { fx: 'dark' }),
  L('q', 'Sorularım@93.7 fazla,@94.7', { fx: 'qmarks' }),
  L('q', 'Neden?@95.0', { fx: 'stamp' }),
  L('q', 'Bunu@95.3 yaptın@96.0 bana?@97.2'),
  L('q', 'Nasıl,@98.0 aşıktım@98.6 sana@99.5', { fx: 'brokenheart', accent: ['aşıktım'] }),
  L('q', 'Bak,@100.1 bak,@100.6 benden@101.0 geriye@101.7 ne@102.2 kaldı?@102.4', { fx: 'crumble' }),
  L('q', 'Sorularım@102.9 fazla@103.9', { fx: 'qmarks' }),
  L('q', 'Neden?@104.2', { fx: 'stamp' }),
  L('q', 'Bunu@104.6 yaptın@105.6 bana?@106.3'),
  L('q', 'aşıktım@107.7 sana@108.6', { fx: 'brokenheart', accent: ['aşıktım'] }),
  L('q', 'Bak,@109.2 bak,@109.7 benden@110.2 geriye@110.8 ne@111.3 kaldı?@111.5', { fx: 'crumble' }),
  // ---- Chorus 2
  L('ch2', 'Bambaşka@112.1 biri@113.7 oldum,@114.1 oldum.@116.3', { fx: 'split' }),
  L('ch2', 'Bambaşka@117.4 biri@118.4 oldum.@118.7', { fx: 'split' }),
  L('ch2', 'Bambaşka@121.3 biri@122.8', { fx: 'split' }),
  L('ch2', 'Bambaşka@123.4 biri@125.0', { fx: 'split' }),
  L('ch2', 'Bambaşka@125.6 biri@127.4 oldum,@127.8 oldum.@129.2', { fx: 'split' }),
  L('ch2', 'Bambaşka@129.9 biri@132.0', { fx: 'split' }),
  L('ch2', 'Bambaşka@132.4 biri@134.3', { fx: 'split' }),
  L('ch2', 'Bambaşka@134.8 biri@136.5 oldum.@137.0', { fx: 'split', end: 138.6 }),
  // ---- Bridge
  L('br', 'Senin@137.9 yüzünden,@139.3', { fx: 'head' }),
  L('br', 'kafamda@140.4 çelişen@142.1', { fx: 'head' }),
  L('br', 'hatıralar,@143.0 karanlıklar,@145.2 pişmanlıklar@146.3', { fx: 'clash' }),
  L('br', 'Senin@147.0 yüzünden,@148.6', { fx: 'head' }),
  L('br', 'kafamda@149.8 çelişen@151.3', { fx: 'head' }),
  L('br', 'hatıralar,@152.1 karanlıklar,@154.3', { fx: 'clash' }),
  L('br', 'pişmanlıkta@155.4 aydınlık@156.6 var@157.5', { fx: 'sun', accent: ['aydınlık'], end: 160.1 }),
  // ---- Final chorus
  L('fin', 'Bambaşka@160.3 biri@161.7', { fx: 'split' }),
  L('fin', 'Bambaşka@162.1 biri,@164.0', { fx: 'split' }),
  L('fin', 'Bambaşka@164.3 biri@166.2 oldum@166.6', { fx: 'split' }),
  L('fin', 'Bambaşka@168.7 biri,@170.8', { fx: 'split' }),
  L('fin', 'bambaşka..@171.2', { fx: 'echo', end: 177.4 }),
];

// backing / echo lines: shown between the lead line they follow and the next lead line
const backingAnchors = [
  ['senin yüzünden', 18], ['Kaderle her gece savaştım', 19], ['Seni artık umursamam aşkım', 20],
  ['Kaderle her gece savaştım', 22], ['Seni artık umursamam aşkım', 23],
  ['nasıl yaptın bana', 38],
  ['senin yüzünden', 42], ['Kaderle her gece savaştım', 43], ['Seni artık umursamam aşkım', 44],
  ['Kaderle her gece savaştım', 46], ['Seni artık umursamam aşkım', 47],
  ['Kaderle her gece savaştım', 56], ['Seni artık umursamam aşkım', 57],
];

// Precise word times: CTC forced alignment (align/aligned.json) of these lyrics on the vocal stem.
const fs = require('fs');
const AL = JSON.parse(fs.readFileSync(require('path').join(__dirname, '..', 'align', 'aligned.json'), 'utf8'));
lines.forEach((l, i) => {
  l.words.forEach((w, k) => { w.t = AL[i][k].s; w.e = AL[i][k].e; });
  l.t = l.words[0].t;
});
const backing = backingAnchors.map(([text, li]) => {
  const L = lines[li], N = lines[li + 1];
  const t0 = L.words[L.words.length - 1].e + 0.05;
  const t1 = Math.max(N.t + 0.3, t0 + 1.3);
  return { text, t0, t1, icon: /Kaderle/.test(text) ? 'swords' : /Seni artık/.test(text) ? 'heartbreak' : null };
});

module.exports = { lines, backing, DURATION: 186.29, TITLE: 'Bambaşka biri' };
