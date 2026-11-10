FPS=30
# id, round, src_in, src_out | (id, round, "hold"/"freeze", seconds) = freeze of previous frame
SEGS=[
# cold open = the whole Natavan round ("laqeyddir")
("T1","natavan",108.70,110.45),("T2","natavan",111.40,115.03),("TT","title","hold",0.9),
("N1","nigar",68.95,71.30),("N2","nigar",75.55,76.95),("HN","nigar","hold",0.45),
("A1","aygun",5.09,7.22),("A2","aygun",7.80,10.38),("HA","aygun","hold",0.3),
("Y1","ayaz",10.40,12.63),("Y2","ayaz",17.40,19.60),("Y3","ayaz",20.45,22.03),("HY","ayaz","hold",0.7),
("R1","roya",61.11,64.30),("R2","roya",64.48,68.85),
("Z1","roza",38.00,41.05),("Z2","roza",43.48,48.42),("FZ","roza","freeze",1.1),("Z3","roza",50.03,53.15),
("S1","samra",80.00,82.30),("S2","samra",83.85,85.76),("S3","samra",86.30,88.25),("S4","samra",89.03,92.60),("S5","samra",93.86,95.30),("HS","samra","hold",0.6),
("P1","promete",95.30,97.05),("P2","promete",101.62,108.00),
("Q1","zamiq",115.03,117.15),("Q3","zamiq",128.72,131.30),
("U1","nuran",165.45,167.55),("U2","nuran",191.85,195.75),
("E1","elza",132.10,134.80),("E1b","elza",136.25,137.04),("E2","elza",147.40,154.00),("E4","elza",161.05,164.72),("FE","elza","freeze",2.8),
]
def timeline():
  out=[];t=0.0
  for s in SEGS:
    if s[2] in ("freeze","hold"):
      n=round(s[3]*FPS); out.append(dict(id=s[0],round=s[1],freeze=True,kind=s[2],src=out[-1]["src_out"]-1/FPS,ostart=t,odur=n/FPS))
    else:
      n=round((s[3]-s[2])*FPS); out.append(dict(id=s[0],round=s[1],freeze=False,src_in=s[2],src_out=s[2]+n/FPS,ostart=t,odur=n/FPS))
    t+=n/FPS
  return out,t
def m(src, prefer=None):
  tl,_=timeline()
  cands=[s for s in tl if not s["freeze"] and s["src_in"]-0.06<=src<=s["src_out"]+0.06]
  if prefer: cands=[s for s in cands if s["id"].startswith(prefer)] or cands
  if not cands: raise ValueError(src)
  s=cands[0]; return round(s["ostart"]+min(max(src-s["src_in"],0),s["odur"]),3)
