import mido, random
random.seed(7)
TPB=480; S16=120; SW=16
mid=mido.MidiFile(ticks_per_beat=TPB)
ev=[]  # (tick, msg)
def note(ch,n,step,dur,vel,bar):
    t=bar*16*S16+int(step*S16)+(SW if int(step)%2==1 and step==int(step) else 0)
    t+=random.randint(-3,3) if ch!=9 else 0; t=max(0,t)
    ev.append((t,mido.Message('note_on',channel=ch,note=n,velocity=max(1,min(127,vel+random.randint(-5,5))))))
    ev.append((t+int(dur*S16),mido.Message('note_off',channel=ch,note=n,velocity=0)))
progs={0:33,1:27,2:7,3:61,4:17,5:28}
vols={0:118,1:84,2:88,3:96,4:52,5:70,9:112}
pans={0:64,1:40,2:92,3:64,4:64,5:86,9:64}
for ch,p in progs.items(): ev.append((0,mido.Message('program_change',channel=ch,program=p)))
for ch,v in vols.items(): ev.append((0,mido.Message('control_change',channel=ch,control=7,value=v))); ev.append((0,mido.Message('control_change',channel=ch,control=10,value=pans[ch]))); ev.append((0,mido.Message('control_change',channel=ch,control=91,value=28)))
K,SN,HH,OH,CR,CL,CB,TB=36,38,42,46,49,39,56,54
def drums(bar,upto=16,cow=False,tamb=False):
    for s in range(upto):
        if s in (0,7,8,10): note(9,K,s,1,112 if s in(0,8) else 92,bar)
        if s in (4,12): note(9,SN,s,1,108,bar); note(9,CL,s,1,60,bar)
        if s in (6,9,15): note(9,SN,s,1,34,bar)
        if s==14: note(9,OH,s,1.5,78,bar)
        else: note(9,HH,s,1,86 if s%4==0 else (62 if s%2==0 else 44),bar)
        if cow and s%4==0: note(9,CB,s,1,48,bar)
        if tamb and s%2==1: note(9,TB,s,1,40,bar)
E1,G1,A1,B1,D2,E2,G2,A2=28,31,33,35,38,40,43,45
bassX=[(0,2.5,E1,112),(3,.8,E1,92),(6,.8,G1,96),(7,.9,A1,100),(10,.6,E2,112),(11,.6,D2,90),(12,1.5,E1,108),(14,.7,B1,92),(15,.7,D2,96)]
bassY=[(0,2.5,A1,112),(3,.8,A1,92),(6,.8,E2,96),(7,.9,G2,100),(10,.6,A2,112),(11,.6,G2,90),(12,1.5,A1,106),(14,.7,D2,94),(15,.7,39,98)]
EM=[55,59,62,66]; A13=[55,61,66,57]
def band(bar,kind,upto=16,clav=False,organ=False):
    for s,d,n,v in (bassX if kind=='X' else bassY):
        if s<upto: note(0,n,s,d,v,bar)
    ch=EM if kind=='X' else A13
    for s in (2,5,10,13):
        if s<upto:
            for n in ch: note(1,n,s,.7,84,bar)
    for s in range(upto):
        if s not in (2,5,10,13) and s%2==1: note(5,52 if kind=='X' else 57,s,.4,46,bar)
    if clav:
        lick=[(8,59),(9,62),(10,64),(12,67),(13,64),(14,62),(15,59)] if kind=='X' else [(8,61),(9,64),(10,66),(12,69),(13,66),(14,64),(15,62)]
        for s,n in lick:
            if s<upto: note(2,n,s,.7,92,bar)
    if organ and upto==16:
        for n in ([52,55,59,62] if kind=='X' else [52,55,57,61]): note(4,n,0,15,60,bar)
def stab(bar,step,dur,vel=112,top=0):
    for n in (52,64,67,71,74+top): note(3,n,step,dur,vel,bar)
    note(9,CR,step,4,104,bar); note(9,K,step,1,120,bar)
# bar0
stab(0,0,1.6); drums(0); band(0,'X')
# bar1: groove half, fill, hit at step 12, stop
drums(1,8); band(1,'Y',8)
for s,n,v in [(8,SN,70),(9,SN,84),(10,50,96),(10.5,50,80),(11,45,104),(11.5,SN,100)]: note(9,n,s,1,v,1)
stab(1,12,1.4,120); note(0,E1,12,1.4,120,1)
for n in EM: note(1,n,12,1.2,100,1)
note(9,OH,15,1,60,1)
# bars 2-5
for b,k in [(2,'X'),(3,'Y'),(4,'X'),(5,'Y')]:
    drums(b,cow=b>=4,tamb=True); band(b,k,clav=True,organ=True)
    if b>=4:
        for n in (64,67,71): note(3,n,0,.8,96,b); note(3,n,3,.6,84,b)
        note(3,74,14,.6,88,b); note(3,76,15,.9,96,b)
note(9,CR,0,4,90,2); note(9,CR,0,4,90,4)
# bar6 ending
drums(6,8,cow=True,tamb=True); band(6,'X',8,clav=False)
for i,(nb,nc) in enumerate([(E1,64),(G1,67),(A1,69),(B1,71)]):
    note(0,nb+12,8+i,.8,112,6); note(2,nc,8+i,.8,104,6); note(3,nc,8+i,.8,100,6); note(9,SN,8+i,1,70+i*12,6)
stab(6,12,5,124,2); note(0,E1,12,5,124,6)
for n in EM: note(1,n,12,4,104,6)
for n in (52,59,64): note(4,n,12,5,80,6)
ev.sort(key=lambda e:(e[0],e[1].type!='note_off'))
tr=mido.MidiTrack(); mid.tracks.append(tr); tr.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(119)))
last=0
for t,m in ev: tr.append(m.copy(time=t-last)); last=t
tr.append(mido.MetaMessage('end_of_track',time=TPB*3))
mid.save('funk.mid')
