import json
T0=12.5
L=[
("Molla Vəli Vidadi yazırdı:",[12.80,13.44,13.72,14.12],14.6),
("Siyah tellər ağ buxağın yanına,",[14.78,15.70,16.22,16.48,17.10],17.6),
("Xırda tellər zənəxdana düşübdü.",[17.70,18.50,19.16,19.94],20.5),
("Bəli, bu günün sözü elə bu misradakı zənəxdandır.",[20.50,21.46,21.85,22.22,22.70,23.16,23.34,24.20],24.9),
("Zənəxdan elə bildiyimiz qəmzədir, yəni güləndə üzdə yaranan o incə cizgidir.",[25.00,26.06,26.22,26.72,27.42,27.86,28.42,28.86,29.34,29.66,30.16],30.66),
("Səhər-səhər işə tələsəndə, tıxacda qalanda, bəzən istər-istəməz qaşqabağımız yerlə gedir.",[31.28,32.00,32.22,32.90,33.40,34.02,34.76,35.54,36.46,36.88],37.18),
("Halbuki qapalı qapıları açan, ən çətin vəziyyəti belə yumşaldan, ən güclü silahımız elə səmimi bir təbəssümdür.",[37.10,37.88,38.80,39.28,39.78,40.30,40.68,41.08,41.32,42.00,42.58,42.92,43.42,43.96,44.42,44.62],45.62),
("Gərginliyi həll etmək üçün çox vaxt uzun sözlərə ehtiyac qalmır.",[46.14,46.60,46.86,47.16,47.50,47.98,48.20,48.46,48.84,49.32],49.76),
("Sadəcə gülümsəmək bəs edir.",[50.10,50.74,51.44,51.72],52.0),
("Sözümün canı odur ki, gündəlik qayğılar sizi özünüzdən uzaqlaşdırmasın.",[52.40,52.80,53.10,53.38,53.62,54.36,54.88,55.12,55.78],56.8),
("Üzünüzdən o şirin zənəxdan, yəni qəmzə heç vaxt silinməsin.",[57.04,57.84,58.00,58.36,58.96,59.56,59.96,60.58,60.90],61.6),
("Söz yerinə düşdü. Gələn sözlərə qədər.",[62.92,63.88,64.36,64.88,65.76,66.42],66.9),
("Sözümün canı.",[68.35,68.95],69.6)]
out=[];md=["# Sözümün Canı — «Zənəxdan» — transkript (montaj vaxtı)\n","Giriş (açılış «Sözümün canı», atalar sözü və «qulağınız bizdə olsun», orijinalda 0:00–0:12.5) çıxarılıb; video Vidadinin misraları ilə başlayır.\n"]
f=lambda x:f"{int(x//60):02d}:{x%60:05.2f}"
for txt,ts,e in L:
    ws=txt.split(); assert len(ws)==len(ts),(txt,len(ws),len(ts))
    out.append({"s":round(ts[0]-T0,2),"e":round(e-T0,2),"text":txt,"w":[[w,round(t-T0,2)] for w,t in zip(ws,ts)]})
    md.append(f"`{f(ts[0]-T0)} – {f(e-T0)}`  {txt}  ")
open('proj/data.js','w').write("const T0="+str(T0)+";const LINES="+json.dumps(out,ensure_ascii=False)+";")
open('proj/transcript_az.md','w').write("\n".join(md)+"\n"); print(open('proj/transcript_az.md').read())
