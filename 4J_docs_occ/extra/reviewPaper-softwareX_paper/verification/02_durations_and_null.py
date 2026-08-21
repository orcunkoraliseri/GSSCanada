import math,random,statistics,csv
from datetime import datetime,timedelta
from occupant_agent.grounding.scheduler import ActivityScheduler,_CATEGORY_NAMES,_get_category
CATS=_CATEGORY_NAMES;K=len(CATS);EPS=1e-9
START=datetime(2023,1,2);NDAYS=180;STEPS=96;DT=15
DATA="bo_env/Lib/site-packages/occupant_agent/data/"
def kl(P,Q): return sum(p*math.log(p/(q+EPS)) for p,q in zip(P,Q) if p>0)

print("REAL ATUS mean episode duration vs SIMULATED, per stratum (min)")
print("real = weighted mean of mean_duration_min over the tier-3 codes in each")
print("       category, from the package's own activity_frequency_<S>.csv\n")
rep={"O1":0.0181,"O2":0.0253,"O3":0.0184,"O4":0.0092}
for strat in ("O1","O2","O3","O4"):
    # real durations from shipped file
    real={}
    for r in csv.DictReader(open(DATA+"activity_frequency_%s.csv"%strat,encoding="utf-8")):
        c=_get_category(r["trcode"]); w=float(r["n_episodes"]); d=float(r["mean_duration_min"])
        a,b=real.get(c,(0.0,0.0)); real[c]=(a+w*d,b+w)
    real={c:(v[0]/v[1]) for c,v in real.items() if v[1]>0}
    # simulated
    sch=ActivityScheduler(strat,seed=42); t=START; cats=[]
    for i in range(NDAYS*STEPS):
        cats.append(_get_category(sch.sample(t))); t+=timedelta(minutes=DT)
    runs={};cur=cats[0];n=1
    for c in cats[1:]:
        if c==cur:n+=1
        else: runs.setdefault(cur,[]).append(n*DT);cur=c;n=1
    runs.setdefault(cur,[]).append(n*DT)
    tr=[sum(1 for a,b in zip(cats[d*STEPS:(d+1)*STEPS],cats[d*STEPS+1:(d+1)*STEPS]) if a!=b) for d in range(NDAYS)]
    print("### %s   transitions/day = %.1f"%(strat,statistics.mean(tr)))
    print("     %-11s %9s %9s %8s"%("category","real","sim","ratio"))
    for c in CATS:
        if c in real and c in runs and len(runs[c])>3:
            s=statistics.mean(runs[c])
            print("     %-11s %9.1f %9.1f   %5.2fx"%(c,real[c],s,real[c]/s))
    # null under both readings of n
    out=[]
    for lab,(wd,we) in {"129/51 calendar":(129,51),"180/180":(180,180)}.items():
        rng=random.Random(7);nulls=[]
        for _ in range(300):
            tot=0.0;cells=0
            for dt_,nd in (("weekday",wd),("weekend",we)):
                base=START if dt_=="weekday" else START+timedelta(days=5)
                for h in range(24):
                    w=sch.category_weights(h,base.replace(hour=h))
                    P=[w.get(c,0.0) for c in CATS];s=sum(P)
                    if s<=0:continue
                    P=[p/s for p in P];nn=nd*4
                    dr=rng.choices(range(K),weights=P,k=nn)
                    tot+=kl(P,[dr.count(j)/nn for j in range(K)]);cells+=1
            nulls.append(tot/cells)
        nulls.sort()
        out.append("%s: null mean %.4f  95%% [%.4f, %.4f]"%(lab,statistics.mean(nulls),nulls[7],nulls[292]))
    print("     reported Tier-1 = %.4f nats"%rep[strat])
    for o in out: print("       "+o)
    print()
