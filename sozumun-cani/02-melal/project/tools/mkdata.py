import json,difflib,re
T0=12.78
tr=json.load(open('trv.json'))
ww=[(w,s,e) for seg in tr for (w,s,e) in seg['words'] if s>=T0-0.1]
fixed=[
"Bu günün sözü məlaldır.",
"Ərəb dilindən dilimizə keçən bu şairanə və kübar sözün mənası kədər, sıxıntı, qəlb yorğunluğu deməkdir.",
"Lakin bu sadəcə fiziki yorğunluq deyil, tamamilə bir könül məsələsidir.",
"İndi biz bu hala stres və ya depressiya deyib, dərhal dərman atırıq ki, tez keçib getsin.",
"Halbuki qədim insanlar bu duyğuya bir başqa hörmətlə yanaşıblar.",
"Onlar bilirdilər ki, məlal insanın dünyanın səs-küyündən bezib öz içinə çəkilməsi, özü ilə baş-başa qalmasıdır.",
"Bu bir boşluq deyil, əslində doluluqdur.",
"İnsanın ürəyi o qədər sözlə dolar ki, danışmağa taqəti qalmaz.",
"Bax, məlal həmin o sükutun adıdır və ancaq dərin adamlara yaraşır.",
"Sözümün canı odur ki, əgər bu gün ürəyinizdə bir məlal varsa, ondan qorxmayın.",
"Çünki məlal əslində ruhunuzun sizinlə ən səmimi və ən səssiz söhbətidir.",
"Söz yerinə düşdü. Gələn sözlərə qədər.",
"Sözümün canı."]
norm=lambda s:re.sub(r'[^\wəıöüşçğ]','',s.lower())
F=[(i,w) for i,l in enumerate(fixed) for w in l.split()]
# whisper words: split hyphen-joined pieces were separate tokens; merge tokens starting with '-'
W=[]
for w,s,e in ww:
    if w.startswith('-') and W: W[-1]=(W[-1][0]+w,W[-1][1],e)
    else: W.append((w,s,e))
sm=difflib.SequenceMatcher(None,[norm(w) for _,w in F],[norm(w) for w,_,_ in W],autojunk=False)
times=[None]*len(F)
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=='equal':
        for k in range(i2-i1): times[i1+k]=W[j1+k][1]
    elif tag=='replace':
        a=W[j1][1]; b=W[j2-1][2]
        for k in range(i2-i1): times[i1+k]=a+(b-a)*k/(i2-i1)
# fill remaining by interpolation
for k in range(len(times)):
    if times[k] is None:
        p=k-1; n=k+1
        while n<len(times) and times[n] is None: n+=1
        times[k]=(times[p]+0.25) if n>=len(times) else (times[p]+times[n])/2
out=[];md=["# Sözümün Canı — «Məlal» — transkript (montaj vaxtı)\n","Giriş (atalar sözü və «qulağınız bizdə olsun», orijinalda 0:00–0:12.8) çıxarılıb.\n"]
for i,l in enumerate(fixed):
    ws=[(w,round(times[k]-T0,2)) for k,(li,w) in enumerate(F) if li==i]
    segE=max(e for w,s,e in W if s-T0<=ws[-1][1]+0.01)-T0 if i<len(fixed) else 0
    e=[x for x in W if abs(x[1]-T0-ws[-1][1])<0.01]; end=(e[0][2]-T0) if e else ws[-1][1]+0.5
    out.append({"s":ws[0][1],"e":round(end,2),"text":l,"w":ws})
    f=lambda x:f"{int(x//60):02d}:{x%60:05.2f}"
    md.append(f"`{f(ws[0][1])} – {f(end)}`  {l}  ")
open('proj/data.js','w').write("const T0="+str(T0)+";const LINES="+json.dumps(out,ensure_ascii=False)+";")
open('proj/transcript_az.md','w').write("\n".join(md)+"\n")
for o in out: print(o['s'],o['e'],' '.join(f"{w}@{t}" for w,t in o['w']))
