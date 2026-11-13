import json, sys, numpy as np
W = sys.argv[1].rstrip('/\') + '/'          # folder written by extract.py
R = json.load(open(sys.argv[2], encoding="utf-8"))   # results/results.json
def load(l,y):
    d=np.load(W+f"{l}_{y}.npz"); return d["Z"],d["x"],str(list(d["codes"]))
def tabs(l,years):
    T={y:load(l,y) for y in years}
    keep=np.all([T[y][1]>0 for y in years],axis=0)
    idx=np.flatnonzero(keep)
    return {y:(T[y][0][np.ix_(idx,idx)],T[y][1][idx]) for y in years}, idx, (~keep).sum()
def fw(Z,x): return x-Z.sum(1), x-Z.sum(0)
def hind(Z0,x0,f1,w1):
    A=Z0/x0[None,:]; B=Z0/x0[:,None]; I=np.eye(len(x0))
    return np.linalg.solve(I-A,f1), np.linalg.solve((I-B).T,w1)
def ras(z0,rt,ct,it=1000):
    z=z0.copy()
    for k in range(it):
        rs=z.sum(1); z=z*np.where(rs>0,rt/np.where(rs>0,rs,1),1)[:,None]
        cs=z.sum(0); z=z*np.where(cs>0,ct/np.where(cs>0,cs,1),1)[None,:]
        err=max(np.abs(z.sum(1)-rt).max(),np.abs(z.sum(0)-ct).max())
        if err<=1e-9*max(1,rt.sum()): break
    return z,err,k+1
BASES={"2015":range(2015,2020),"2020":range(2020,2025)}
def run(l, collect_t3=True):
    out={}
    for b,ys in BASES.items():
        ys=list(ys); T,idx,nd=tabs(l,ys)
        for i in range(4):
            y0,y1=ys[i],ys[i+1]; Z0,x0=T[y0]; Z1,x1=T[y1]
            f0,w0=fw(Z0,x0); f1,w1=fw(Z1,x1)
            L,G=hind(Z0,x0,f1,w1)
            p={"leontief":L,"ghosh":G,"N":x0,"U":x0*x1.sum()/x0.sum(),"DL":x0+f1-f0,"DG":x0+w1-w0}
            num={k:np.abs(v-x1).sum() for k,v in p.items()}; den=x1.sum()
            A=Z0/x0[None,:];B=Z0/x0[:,None]
            zl=np.abs(A*x1[None,:]-Z1).sum(); zg=np.abs(B*x1[:,None]-Z1).sum(); zd=Z1.sum()
            zr,err,its=ras(Z0,Z1.sum(1),Z1.sum(0))
            e={"num":num,"den":den,"z":(zl,zg,np.abs(zr-Z1).sum(),zd),"ras":(err,its)}
            if i>=1:
                fm,wm=fw(*T[ys[i-1]]); xm=T[ys[i-1]][1]
                L3,G3=hind(Z0,x0,2*f0-fm,2*w0-wm)
                p3={"leontief":L3,"ghosh":G3,"T":2*x0-xm,"N":x0}
                e["t3"]={k:np.abs(v-x1).sum()/den for k,v in p3.items()}
            out[f"{y0}-{str(y1)[2:]}"]=e
    return out
if __name__=="__main__":
    o=run("83"); P=R["main_83_current_prices"]
    md=0; rows=[]
    for t,e in o.items():
        pt=P["per_transition"][t]
        for k in ("leontief","ghosh","U","N","DL","DG"):
            md=max(md,abs(e["num"][k]/e["den"]-pt[f"wape_x_{k}"]))
        md=max(md,abs(e["z"][0]/e["z"][3]-pt["wape_z_leontief"]),abs(e["z"][1]/e["z"][3]-pt["wape_z_ghosh"]))
        r=np.log(e["num"]["ghosh"]/e["num"]["leontief"]); md=max(md,abs(r-pt["r"]))
        print(t,"r",round(r,6),pt["r"], "ras_err/its",e["ras"], "zras",e["z"][2]/e["z"][3],pt["wape_z_ras"])
        md=max(md,abs(e["z"][2]/e["z"][3]-pt["wape_z_ras"]))
    print("task1 per-transition max abs diff",md)
    po=P["pooled"]; d2=0
    sn={k:sum(e["num"][k] for e in o.values()) for k in ("leontief","ghosh","U","N","DL","DG")}; sd=sum(e["den"] for e in o.values())
    for k in sn: d2=max(d2,abs(sn[k]/sd-po[f"wape_x_{k}"]))
    pr=np.log(sn["ghosh"]/sn["leontief"]); d2=max(d2,abs(pr-P["point"]["H1_r"]))
    zs=lambda j:sum(e["z"][j] for e in o.values())/sum(e["z"][3] for e in o.values())
    d2=max(d2,abs(zs(0)-po["wape_z_leontief"]),abs(zs(1)-po["wape_z_ghosh"]),abs(zs(2)-po["wape_z_ras"]))
    print("pooled max diff",d2,"H1_r",pr,P["point"]["H1_r"])
    # T3
    d3=0
    for t,e in o.items():
        if "t3" in e:
            for k in ("leontief","ghosh","T","N"): d3=max(d3,abs(e["t3"][k]-P["per_transition"][t][f"t3_wape_x_{k}"]))
            print(t,"t3",{k:round(v,6) for k,v in e["t3"].items()})
    print("task2 T3 max diff all six",d3)
    ext=[t for t in ("2016-17","2017-18","2018-19","2022-23","2023-24")]
    c=lambda j:sum(o[t]["z"][j] for t in ext)/sum(o[t]["z"][3] for t in ext)
    print("compilation",c(0),c(1),c(2),P["pooled"]["compilation"])
    # 165
    o5=run("165"); 
    for t,e in o5.items(): print("165",t,"ras err,its",e["ras"],"zras",e["z"][2]/e["z"][3])
    json.dump({"ok":1},open("done.json","w"))
