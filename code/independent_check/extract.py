import sys, glob, os, re, numpy as np
from openpyxl import load_workbook
panel=sys.argv[1]; out=sys.argv[2]
for p in sorted(glob.glob(os.path.join(panel,"*.xlsx"))):
    nm=os.path.basename(p)
    m=re.search(r"(20\d\d)",nm); yr=m.group(1)
    lvl="83" if "중분류" in nm else "165"
    wb=load_workbook(p,read_only=True,data_only=True)
    sh=[s for s in wb.sheetnames if "국산거래표" in s]
    assert len(sh)==1,(nm,wb.sheetnames)
    rows=[list(r) for r in wb[sh[0]].iter_rows(values_only=True)]
    wb.close()
    def c(v):
        if v is None: return ""
        if isinstance(v,float) and v.is_integer(): v=int(v)
        return str(v).strip()
    hi=next(i for i,r in enumerate(rows[:30]) if "9290" in [c(v) for v in r])
    hdr=[c(v) for v in rows[hi]]
    secc=[(h,j) for j,h in enumerate(hdr) if re.fullmatch(r"\d{2,3}",h) and h not in ("9090",)]
    # sector columns: those before 9090
    j9090=hdr.index("9090")
    secc=[(h,j) for h,j in secc if j<j9090]
    codes=[h for h,_ in secc]
    rowd={}
    for r in rows[hi+1:]:
        k=c(r[0]) if r else ""
        if k in codes and k not in rowd: rowd[k]=r
    assert set(rowd)==set(codes),(nm,len(codes),len(rowd))
    Z=np.array([[float(rowd[a][j]) for _,j in secc] for a in codes])
    x=np.array([float(rowd[a][hdr.index("9290")]) for a in codes])
    fd=np.array([float(rowd[a][hdr.index("9190")]) for a in codes])
    np.savez(os.path.join(out,f"{lvl}_{yr}.npz"),Z=Z,x=x,fd=fd,codes=np.array(codes))
    print(nm,lvl,yr,len(codes),float(np.abs(Z.sum(1)+fd-x).max()/x.min()),flush=True)
