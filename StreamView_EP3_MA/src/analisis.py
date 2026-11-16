"""StreamView Analytics - análisis reproducible (EP5, ADY1104).
Uso: python src/analisis.py  (desde la carpeta del proyecto). Genera src/results.json."""
import pandas as pd, numpy as np, json, os
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m=pd.read_csv(f"{B}/data/netflix_movies_detailed_up_to_2025.csv");t=pd.read_csv(f"{B}/data/netflix_tv_shows_detailed_up_to_2025.csv")
m["fmt"]="Películas";t["fmt"]="Series";a=pd.concat([m,t],ignore_index=True)
a["views"]=a.popularity*1000          # visualizaciones = popularity x 1000 (suma 1.363,8 M)
tot=a.views.sum()
GEN={"Drama":"Drama","Comedy":"Comedia","Action":"Acción","Animation":"Animación","Documentary":"Documental"}
a["g"]=a.genres.fillna("").str.split(",").str[0].str.strip().map(GEN).fillna("Otros")
a["c"]=a.country.fillna("").str.split(",").str[0].str.strip()
rated=a[a.rating>0]
R={"n":len(a),"views_M":tot/1e6,"sin_rating":int((a.rating==0).sum()),"rating_med":float(rated.rating.median())}
def top10(v):v=np.sort(v.values);return float(v[-max(1,int(len(v)*.1)):].sum()/v.sum()*100)
def roi(d):d=d[(d.revenue>0)&(d.budget>0)];return float((d.revenue/d.budget).median()) if len(d) else None
K={}
for f in ["Todos","Películas","Series"]:
    for g in ["Todos"]+list(GEN.values()):
        d=a if f=="Todos" else a[a.fmt==f]; d=d if g=="Todos" else d[d.g==g]
        K[f"{f}|{g}"]=[len(d),round(d.views.sum()/1e6,1),round(float(d[d.rating>0].rating.median()),2) if (d.rating>0).any() else None,roi(d[d.fmt=="Películas"]),round(top10(d.views),1) if len(d)>9 else None]
R["kpi"]=K
gg=a.groupby("g").agg(n=("views","size"),v=("views","sum"));gg["pc"]=gg.n/len(a)*100;gg["pv"]=gg.v/tot*100
gg["med"]=rated.groupby("g").rating.median()
R["generos"]={g:[round(gg.loc[g,"pc"],1),round(gg.loc[g,"pv"],1),round(float(gg.loc[g,"med"]),2)] for g in GEN.values()}
L=a.groupby("language").views.sum().sort_values(ascending=False)/tot*100;R["idiomas_top"]={k:round(v,1) for k,v in L.head(6).items()}
sp={"United States of America":"EE. UU.","United Kingdom":"Reino Unido","South Korea":"Corea del Sur","Spain":"España","Japan":"Japón","India":"India","Canada":"Canadá","":"Sin país informado"}
C=a.groupby("c").views.sum()/tot*100;R["paises"]=[[sp[k],round(float(C.get(k,0)),1)] for k in sp]
R["paises_top8_real"]={k:round(v,1) for k,v in C.sort_values(ascending=False).head(8).items()}
s=a.views.sort_values().values;q=np.array_split(s,4)
R["cola"]={"mediana":float(np.median(s)),"promedio":float(s.mean()),"top10":top10(a.views),"q1_max":float(q[0].max()),"q":[round(float(x.sum()/s.sum()*100),1) for x in q]}
mm=m[m.revenue>0];R["pel_con_ingresos"]=len(mm);R["roi_med"]=roi(m)
b=pd.cut(mm.rating,[-1,5,6,7,7.5,8,11],right=False);R["bandas"]=(mm.groupby(b,observed=False).revenue.sum()/mm.revenue.sum()*100).round(1).tolist()
R["rev_ge75"]=float(mm[mm.rating>=7.5].revenue.sum()/mm.revenue.sum()*100)
R["duracion_pel_disponible"]=int(m.duration.notna().sum())
json.dump(R,open(f"{B}/src/results.json","w"),ensure_ascii=False,indent=1)
print(json.dumps({k:v for k,v in R.items() if k!="kpi"},ensure_ascii=False));print(a.language.value_counts().head(6).to_dict())
print(K["Todos|Todos"],K["Películas|Todos"],K["Series|Todos"],K["Todos|Acción"])

# --- Evidencia adicional para recomendación (causas e impacto)
from scipy.stats import spearmanr
E={}
r=a[a.rating>0];E["spearman_rating_vistas"]=float(spearmanr(r.rating,r.views)[0])
E["rating_igual_vote_average"]=bool((a[a.rating>0].rating.round(1)==a[a.rating>0].vote_average.round(1)).mean()>0.99)
alto=r[r.rating>=7.5];E["alto_pct_titulos"]=round(len(alto)/len(r)*100,1);E["alto_pct_vistas"]=round(alto.views.sum()/r.views.sum()*100,1)
med=a.views.median();j=r[(r.rating>=7.5)&(r.views<med)];E["joyas_n"]=len(j);E["joyas_pct_titulos"]=round(len(j)/len(a)*100,1);E["joyas_vistas_M"]=round(j.views.sum()/1e6,1)
E["joyas_pct_series"]=round((j.fmt=="Series").mean()*100,1);E["joyas_uplift_M"]=round((med-j.views).clip(lower=0).sum()/1e6,1);E["joyas_uplift_pct"]=round(E["joyas_uplift_M"]/(tot/1e6)*100,1)
E["mediana_vistas_serie"]=float(a[a.fmt=="Series"].views.median());E["mediana_vistas_pelicula"]=float(a[a.fmt=="Películas"].views.median())
rec=a[a.release_year>=2020];E["rec_pct_titulos"]=round(len(rec)/len(a)*100,1);E["rec_pct_vistas"]=round(rec.views.sum()/tot*100,1)
n=len(a)//10;t10=a.nlargest(n,"views");E["top10_pct_series"]=round((t10.fmt=="Series").mean()*100,1)
R["extra"]=E;json.dump(R,open(f"{B}/src/results.json","w"),ensure_ascii=False,indent=1);print(E)
