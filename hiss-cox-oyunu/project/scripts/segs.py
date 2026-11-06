FPS=30
SEGS=[ # id, round, in, out
("N1","nigar",68.35,71.30),("N2","nigar",71.39,74.96),
("A1","aygun",5.09,7.22),("A2","aygun",7.80,9.97),
("Y1","ayaz",10.27,12.63),("Y2","ayaz",17.40,22.03),
("R1","roya",61.11,64.30),("R2","roya",64.48,68.20),
("Z1","roza",38.00,41.05),("Z2","roza",43.48,48.42),("FZ","roza","freeze",1.0),("Z3","roza",50.03,53.15),
("S1","samra",80.00,82.30),("S2","samra",83.85,85.76),("S3","samra",86.30,87.75),("S4","samra",89.03,92.60),("S5","samra",93.86,95.05),
("P1","promete",95.05,97.05),("P2","promete",101.62,108.00),
("Q1","zamiq",115.03,117.15),("Q2","zamiq",118.89,120.70),("Q3","zamiq",128.72,130.89),
("E1","elza",132.10,137.04),("E2","elza",147.09,154.00),("E4","elza",161.05,164.72),("FE","elza","freeze",2.2),
]
def timeline():
  out=[];t=0.0
  for s in SEGS:
    if s[2]=="freeze":
      n=round(s[3]*FPS); out.append(dict(id=s[0],round=s[1],freeze=True,src=out[-1]["src_out"]-1/FPS,ostart=t,odur=n/FPS))
    else:
      n=round((s[3]-s[2])*FPS); out.append(dict(id=s[0],round=s[1],freeze=False,src_in=s[2],src_out=s[2]+n/FPS,ostart=t,odur=n/FPS))
    t+=n/FPS
  return out,t
def m(src):
  """map source time to output time (first segment containing it)"""
  tl,_=timeline()
  for s in tl:
    if not s["freeze"] and s["src_in"]-0.06<=src<=s["src_out"]+0.06: return round(s["ostart"]+min(max(src-s["src_in"],0),s["odur"]),3)
  raise ValueError(src)
