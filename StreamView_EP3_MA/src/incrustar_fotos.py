"""Incrusta las fotos dentro del HTML para que se vean en cualquier computador, sin carpetas.
Uso:  python incrustar_fotos.py RUTA_DEL_HTML CARPETA_DE_FOTOS
Crea dashboard_con_fotos.html junto al HTML. Cada foto debe llamarse como en el bloque const IMG
(ej. inception.jpg) o como el título (ej. Inception.jpg). Requiere: pip install pillow"""
import sys,re,os,base64,io,json
from PIL import Image
html,carpeta=sys.argv[1],sys.argv[2]
s=open(html,encoding="utf-8").read()
nz=lambda n:re.sub(r"[^a-z0-9]","",n.lower())
bloque=re.search(r"const IMG=\{.*?\n\};",s,re.S).group(0)
tit=dict((t,nz(os.path.splitext(os.path.basename(f))[0])) for t,f in re.findall(r'^\s*"([^"]+)":"([^"]+)"',bloque,re.M))
for t in set(re.findall(r'\["([^"]+)","(?:Películas|Series)"',s)):tit.setdefault(t,nz(t))
datos={};usadas=set()
for f in os.listdir(carpeta):
    r=nz(os.path.splitext(f)[0])
    try:im=Image.open(os.path.join(carpeta,f)).convert("RGB")
    except Exception:continue
    im.thumbnail((420,620));b=io.BytesIO();im.save(b,"JPEG",quality=82)
    for t,k in tit.items():
        if r==k or r==nz(t):datos[t]="data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode();usadas.add(f)
print(len(datos),"fotos incrustadas;","sin usar:",[f for f in os.listdir(carpeta) if f not in usadas])
s=s.replace(bloque,bloque+"\nObject.assign(IMG,"+json.dumps(datos,ensure_ascii=False)+");",1)
out=os.path.join(os.path.dirname(os.path.abspath(html)),"dashboard_con_fotos.html");open(out,"w",encoding="utf-8").write(s);print("Listo:",out)
