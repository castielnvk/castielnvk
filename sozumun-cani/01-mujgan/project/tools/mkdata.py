import json
tr=json.load(open('tr_large-v3.json'))
fixed=[
"Sözümün canı",
"Qulaq gündə bir söz eşitməsə kar olar.",
"Sözümün canı odur ki, qulağınız bizdə olsun.",
"Bu günün sözü müjgandır.",
"Fars dilindən dilimizə keçən bu sözün mənası sadəcə kirpik deməkdir.",
"Lakin klassik ədəbiyyatda bu, bizim bildiyimiz adi kirpik deyil.",
"Aşiqin qəlbinə sancılan oxa bənzədilir.",
"Təsəvvür edin.",
"Göz bir yay, baxış bir atıcı, müjgan isə hədəfi düz onluğundan vuran o oxlardır.",
"İndi xanımlar gözəllik salonunda kirpik qaynağına saatlarla vaxt sərf edirlər ki, baxışları təsirli olsun.",
"Halbuki keçmişdə bütün müdafiələri dağıtmaq üçün bir süzgün baxış və təbii müjgan kifayət edirdi.",
"Yəqin ki, ətrafınızda bu adda xanımlar, bəlkə elə indi sükan arxasında bizi dinləyən bir Müjgan da var.",
"Sözümün canı odur ki, müjgan sadəcə zərif bir qadın adı deyil.",
"O, danışmadan deyilən söz və toxunmadan sancılan oxdur.",
"Çalışın, o oxu kimin qəlbinə atdığınıza həmişə diqqət edin.",
"Söz yerinə düşdü. Gələn sözlərə qədər.",
"Sözümün canı"]
out=[];md=["# Sözümün Canı — «Müjgan» — transkript\n"]
for seg,txt in zip(tr,fixed):
    fw=txt.split(); ww=seg['words']
    if len(fw)==len(ww): times=[w['s'] for w in ww]
    else:
        # manual: line 11 — split merged words
        times=[]; j=0
        m={'bəlkəli':2,'müşqəndə':2}
        for w in ww:
            k=m.get(w['w'].strip().strip('.,'),1)
            for q in range(k): times.append(w['s']+(w['e']-w['s'])*q/k)
    assert len(times)==len(fw),(txt,len(times),len(fw))
    out.append({"s":round(seg['start'],2),"e":round(seg['end'],2),"text":txt,"w":[[a,round(b,2)] for a,b in zip(fw,times)]})
    f=lambda x:f"{int(x//60):02d}:{x%60:05.2f}"
    md.append(f"`{f(seg['start'])} – {f(seg['end'])}`  {txt}  ")
open('proj/data.js','w').write("const LINES="+json.dumps(out,ensure_ascii=False)+";")
open('proj/transcript_az.md','w').write("\n".join(md)+"\n")
print(open('proj/transcript_az.md').read())
