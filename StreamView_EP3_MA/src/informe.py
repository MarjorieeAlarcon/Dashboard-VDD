"""Genera images/*.png, informe_ejecutivo.pdf y resumen_ejecutivo.pdf desde src/results.json."""
import json,os,matplotlib;matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak,Table,TableStyle
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));R=json.load(open(f"{B}/src/results.json"));I=f"{B}/images/"
BG,CY,MG,VI,AM,GR="#0B0220","#22E5F0","#FF3EA5","#A855F7","#FFC857","#A99BCB"
def fig(name,labels,vals,cols,title,unit="%",w=7,h=3.4):
    f,ax=plt.subplots(figsize=(w,h),facecolor=BG);ax.set_facecolor(BG)
    b=ax.barh(labels[::-1],vals[::-1],color=cols[::-1])
    for x,v in zip(b,vals[::-1]):ax.text(v,x.get_y()+x.get_height()/2,f" {v:.1f}".replace(".",",")+unit,va="center",color="#F6F0FF",fontsize=9)
    ax.set_title(title,color=CY,loc="left",fontsize=12,fontweight="bold");ax.tick_params(colors="#F6F0FF");ax.set_xlim(0,max(vals)*1.18)
    [s.set_visible(False) for s in ax.spines.values()];ax.xaxis.set_visible(False);f.tight_layout();f.savefig(I+name,dpi=170,facecolor=BG);plt.close(f)
g=R["generos"];ks=list(g)
fig("g1_series_vs_peliculas.png",["Series: catálogo","Series: vistas","Películas: catálogo","Películas: vistas"],[50,76.1,50,23.9],[GR,CY,GR,MG],"Las series: 50% del catálogo, 76% de las vistas")
fig("g2_generos.png",[f"{k} (catálogo)" for k in ks]+[f"{k} (vistas)" for k in ks],[g[k][0] for k in ks]+[g[k][1] for k in ks],[GR]*5+[VI]*5,"Género: peso en catálogo vs peso en vistas",h=4.6)
fig("g3_rating_genero.png",ks,[g[k][2] for k in ks],[CY if g[k][2]>7 else GR for k in ks],"Rating mediano por género","",h=3)
q=R["cola"]["q"];fig("g4_larga_cola.png",["Q1","Q2","Q3","Q4 (más visto)"],q,[GR,GR,CY,VI],"Larga cola: reparto de vistas por cuartil de títulos")
b=R["bandas"];fig("g5_ingresos_rating.png",["< 5,0","5,0–6,0","6,0–7,0","7,0–7,5","7,5–8,0","≥ 8,0"],b,[GR,CY,CY,CY,MG,MG],"Ingresos de películas por tramo de rating")
fig("g6_paises.png",[p[0] for p in R["paises"]],[p[1] for p in R["paises"]],[VI]+[CY]*7,"Países: % de las visualizaciones")
# --- PDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
D="/usr/share/fonts/truetype/dejavu/";pdfmetrics.registerFont(TTFont("DV",D+"DejaVuSans.ttf"));pdfmetrics.registerFont(TTFont("DVB",D+"DejaVuSans-Bold.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily;registerFontFamily("DV",normal="DV",bold="DVB",italic="DV",boldItalic="DVB")
E_=R["extra"];c=R["cola"];fm=lambda x:f"{x:,.0f}".replace(",",".")
P_="#5B21B6";ss=getSampleStyleSheet()
H=ParagraphStyle("h",fontName="DVB",textColor=colors.HexColor(P_),fontSize=15,leading=19,spaceBefore=8,spaceAfter=6)
H2=ParagraphStyle("h2",fontName="DVB",textColor=colors.HexColor("#0E7490"),fontSize=11.5,leading=15,spaceBefore=6,spaceAfter=3)
N=ParagraphStyle("n",fontName="DV",fontSize=9.5,leading=13.5,spaceAfter=5);T=ParagraphStyle("t",fontName="DVB",fontSize=22,leading=26,textColor=colors.HexColor(P_),spaceAfter=4)
C=ParagraphStyle("c",fontName="DV",fontSize=8,leading=10.5);CB=ParagraphStyle("cb",parent=C,fontName="DVB");CH=ParagraphStyle("ch",parent=CB,textColor=colors.white)
def im(n,w=14):
    from PIL import Image as PI
    iw,ih=PI.open(I+n).size;return Image(I+n,width=w*28.35,height=w*28.35*ih/iw)
def tab(rows,cw,first_bold=True):
    d=[[Paragraph(x,CH) for x in rows[0]]]+[[Paragraph(x,CB if (j==0 and first_bold) else C) for j,x in enumerate(r)] for r in rows[1:]]
    t=Table(d,colWidths=[x*28.35 for x in cw],repeatRows=1);t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor(P_)),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#C4B5FD")),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F5F3FF")])]));return t
def kv(rows):return tab([["Pregunta","Respuesta"]]+rows,[4,13.5])
def P(x):return Paragraph(x,N)
dif=E_["mediana_vistas_serie"]-E_["mediana_vistas_pelicula"]
brief=[Paragraph("Decision brief",H),
 kv([["Decisión","Priorizar series en la adquisición y en la portada, y rescatar las joyas ocultas."],
 ["Contexto",f"StreamView tiene 32.000 títulos (2010–2025) y {R['views_M']:,.1f} M de visualizaciones.".replace(",","X").replace(".",",").replace("X",".")+" La pregunta es dónde conviene invertir catálogo y espacio de portada, porque no se puede promover todo."],
 ["Hallazgo principal","Las series son 50% del catálogo y concentran 76,1% de las vistas. Además tienen mejor nota (mediana 7,2 contra 6,4 en películas)."],
 ["Evidencia",f"La serie mediana tiene {fm(E_['mediana_vistas_serie'])} vistas; la película mediana, {fm(E_['mediana_vistas_pelicula'])}. De los títulos del 10% más visto, {str(E_['top10_pct_series']).replace('.',',')}% son series. El 10% más visto reúne 48,7% de todas las vistas."],
 ["Recomendación","1) Destinar la mayor parte del presupuesto de adquisición a series. 2) Dar portada a las joyas ocultas: títulos con rating ≥ 7,5 y vistas bajo la mediana. 3) Comprar películas con rating entre 6,0 y 8,0, que reúnen 83,9% de los ingresos."],
 ["Impacto esperado",f"Si una serie nueva rinde como la mediana actual, aporta {fm(dif)} vistas más que una película nueva. Las {fm(E_['joyas_n'])} joyas ocultas sumarían {str(E_['joyas_uplift_M']).replace('.',',')} M de vistas (+{str(E_['joyas_uplift_pct']).replace('.',',')}% del total) si llegaran a la mediana. Son escenarios con los datos actuales, no pronósticos."]]),Spacer(1,6)]
S=[Paragraph("StreamView Analytics",T),P("<b>Informe ejecutivo · EP5 Visualización de Datos (ADY1104)</b><br/>Autor/a: [escribe tu nombre]")]+brief+[PageBreak(),
Paragraph("1. Calidad de datos",H),P("El 14,3% de los títulos (4.572) no tiene calificación y se excluye de promedios y medianas. Solo 5.645 películas (35%) reportan ingresos y presupuesto; las series no tienen datos financieros. Las visualizaciones se construyen como popularidad × 1000, lo que suma 1.363,8 millones. El dataset no trae duración de películas ni imágenes, así que no se analiza duración."),
Paragraph("2. Justificación de los KPI",H),P("El dashboard muestra cuatro KPI. Cada uno responde a una decisión distinta; los que no lo hacían se descartaron."),
tab([["KPI (valor global)","Decisión que apoya","Acción que genera","¿Comprensible?","¿Medible?"],
["Visualizaciones (1.363,8 M)","Dónde está el alcance: qué formato o género merece más inversión","Asignar presupuesto de catálogo y portada donde hay audiencia","Sí: es la suma de vistas","Sí: popularidad × 1000 por título, filtrable por formato y género"],
["Rating mediano (6,7)","Qué títulos promover o adquirir","Promover los ≥ 7,5 y revisar los menores a 6,0","Sí: nota típica del catálogo. Se usa mediana porque no la distorsionan los extremos","Sí, excluyendo el 14,3% sin nota"],
["ROI mediano en cine (1,7x)","Qué películas comprar","Priorizar los tramos de rating que recuperan más inversión","Sí: por cada dólar invertido se recuperan 1,7","Sí: ingresos ÷ presupuesto, en 5.645 películas"],
["Concentración Top 10% (48,7%)","Cuánto depende el negocio de pocos éxitos","Dar portada a títulos fuera del top para repartir la audiencia","Sí: el 10% de los títulos reúne casi la mitad de las vistas","Sí: vistas del 10% superior ÷ vistas totales"]],[3.4,3.8,3.8,3.4,3.1]),Spacer(1,4),
P("<b>KPI descartados:</b> total de títulos (no apoya una decisión; queda como contexto bajo Visualizaciones), promedio de vistas (lo distorsionan los éxitos: 42.618 contra una mediana de 22.064), rating promedio (sensible a los títulos sin nota), ingresos totales (solo 35% de las películas tiene dato) y duración (no existe en el dataset)."),
Paragraph("3. Justificación de las visualizaciones",H),
tab([["Gráfico","Patrón que muestra","Por qué facilita la interpretación","Alternativas consideradas","Por qué se descartaron"],
["Series vs películas (barras)","Peso en catálogo contra peso en vistas por formato","Barras alineadas permiten comparar longitudes con precisión","Gráfico de torta; barras apiladas al 100%","La torta dificulta comparar ángulos; las apiladas esconden la comparación directa"],
["Géneros: catálogo vs vistas (barras horizontales)","Géneros que ocupan más catálogo del que se ve, y al revés","Los nombres caben en horizontal y el par de barras muestra la brecha","Torta; treemap; tabla","Demasiados sectores en la torta; el treemap compara mal áreas; la tabla no muestra el patrón"],
["Rating mediano por género (barras)","Qué géneros están mejor valorados","Una sola barra por género, fácil de ordenar mentalmente","Boxplot; radar; promedio","El boxplot es difícil para un público no técnico; el radar confunde; el promedio se distorsiona"],
["Larga cola (barras por cuartil)","Pocos títulos concentran casi todas las vistas","Cuatro barras bastan para ver la desigualdad","Curva de Lorenz; histograma; tabla de percentiles","La curva es más técnica; el histograma queda aplastado por la cola; la tabla no se lee de un vistazo"],
["Ingresos por tramo de rating (barras)","Dónde se concentra la recaudación según la nota","Tramos ordenados dejan ver que el centro (6,0–8,0) domina","Dispersión rating vs ingresos; líneas; gráficos 3D","La dispersión con 5.645 puntos satura; los tramos no son una serie temporal; el 3D distorsiona"],
["Países (barras horizontales, Mayor/Menor)","Mercados que concentran la audiencia","Ranking claro; el botón cambia la métrica sin cambiar el gráfico","Mapa coroplético; burbujas","En el mapa EE. UU. domina y los países pequeños no se ven"]],[3,3.4,3.6,3.7,3.8]),Spacer(1,4),
P("<b>Filtros:</b> se conservan Formato y Género, porque series y películas se comportan muy distinto y el género permite revisar cada línea de contenido. Se descartaron filtros por país, idioma, año y rating: fragmentan los datos y no cambian ninguna decisión. Las únicas tablas son los rankings Top 5, para no saturar."),
im("g1_series_vs_peliculas.png",11),im("g4_larga_cola.png",11),PageBreak(),
Paragraph("4. Recomendación",H),
Paragraph("Acción A: priorizar series",H2),kv([["Qué se observó","Las series son 50% del catálogo y 76,1% de las vistas; su rating mediano es 7,2 contra 6,4."],["Por qué ocurrió","Hipótesis: una serie tiene varios episodios y temporadas, y genera más reproducciones por título. El dataset no mide tiempo de visualización, así que no se puede comprobar. Se descartó el efecto novedad: los títulos desde 2020 son 37,5% del catálogo y 36,9% de las vistas."],["Evidencia",f"Mediana de vistas: {fm(E_['mediana_vistas_serie'])} (series) contra {fm(E_['mediana_vistas_pelicula'])} (películas). {str(E_['top10_pct_series']).replace('.',',')}% del 10% más visto son series."],["Acción que se propone","Destinar la mayor parte del presupuesto de adquisición a series y dar prioridad a series en la portada."],["Impacto esperado",f"{fm(dif)} vistas más por título nuevo, si rinde como la mediana actual."]]),
Paragraph("Acción B: rescatar las joyas ocultas",H2),kv([["Qué se observó",f"{fm(E_['joyas_n'])} títulos ({str(E_['joyas_pct_titulos']).replace('.',',')}% del catálogo) tienen rating ≥ 7,5 y vistas bajo la mediana. El Documental tiene buena nota (7,2) pero solo 2,9% de las vistas."],["Por qué ocurrió","La nota influye poco en la audiencia: la correlación entre rating y vistas es débil ("+str(round(E_['spearman_rating_vistas'],2)).replace('.',',')+"). Un buen título no se descubre solo."],["Evidencia",f"Los títulos con rating ≥ 7,5 son {str(E_['alto_pct_titulos']).replace('.',',')}% de los títulos con nota y {str(E_['alto_pct_vistas']).replace('.',',')}% de las vistas. Las joyas suman solo {str(E_['joyas_vistas_M']).replace('.',',')} M de vistas."],["Acción que se propone","Dar portada y recomendaciones a las joyas, empezando por series y documentales."],["Impacto esperado",f"+{str(E_['joyas_uplift_M']).replace('.',',')} M de vistas (+{str(E_['joyas_uplift_pct']).replace('.',',')}% del total) si llegan a la mediana. Es un impacto modesto, de bajo costo."]]),
Paragraph("Acción C: comprar películas por tramo de rating",H2),kv([["Qué se observó","Los tramos de 6,0 a 8,0 reúnen 83,9% de los ingresos; las películas ≥ 7,5 solo 21,4%."],["Por qué ocurrió","Hipótesis: la recaudación depende más de marketing, franquicia y presupuesto que de la nota de la crítica. El dataset no permite comprobarlo."],["Evidencia","ROI mediano 1,7x en 5.645 películas con ingresos y presupuesto."],["Acción que se propone","No exigir nota alta como único criterio de compra; evaluar películas entre 6,0 y 8,0."],["Impacto esperado","Concentrar la inversión en los tramos que generan 83,9% de la recaudación."]]),
im("g5_ingresos_rating.png",11),PageBreak(),
Paragraph("5. Defensa de la decisión",H),
P("<b>Por qué series.</b> Tres medidas independientes apuntan a lo mismo: su cuota de vistas (76,1% con 50% del catálogo), su mediana de vistas por título (3,3 veces la de películas) y su presencia en el 10% más visto (86,7%). Además tienen mejor nota. No depende de unos pocos éxitos, porque la mediana también las favorece."),
P("<b>Alternativas descartadas.</b> <i>Producir más Acción:</i> tiene la nota más baja (6,23) y rinde menos vistas que su peso (5,0% contra 5,9% del catálogo). <i>Más Drama:</i> ya es 27,1% del catálogo y sus vistas (25,8%) no lo superan. <i>Comprar solo lo mejor valorado:</i> las películas ≥ 7,5 explican solo 21,4% de los ingresos."),
P("<b>Objeciones.</b> «Las series cuestan más»: el dataset no tiene costos de series, por eso la propuesta es priorizar y medir el resultado, no cambiar todo el catálogo. «Popularidad no son vistas»: es un proxy, pero suma 1.363,8 M, coherente con el total del caso, y los resultados se mantienen usando medianas. «El efecto es solo novedad»: se probó y no aparece."),
Paragraph("6. Tres preguntas de presentación",H),
kv([["¿Por qué series si el catálogo es 50 y 50?","Porque las vistas no se reparten igual: 76,1% va a series y la serie mediana tiene 3,3 veces las vistas de una película mediana."],["¿Cómo sabe que son vistas reales?","Son un proxy: popularidad × 1000. La suma coincide con el total de 1.363,8 M y las conclusiones se sostienen con medianas. Lo ideal sería medir horas vistas."],["¿Y si una nota alta no atrae público?","Es lo que muestra el dato: la correlación es débil (0,32). Por eso la acción B usa portada y recomendaciones, y su efecto se mediría con una prueba A/B."]]),
Paragraph("7. Dashboard y limitaciones",H),P("El archivo dashboard/dashboard_streamview.html funciona sin conexión: filtros por Formato y Género, contador de clics, cinco pestañas y vitrina de pósters con opción de destacar y subir una foto propia. Limitaciones: las vistas son un proxy, no hay duración de películas ni costos de series, los pósters son ilustraciones y los motivos de las acciones A y C son hipótesis.")]
SimpleDocTemplate(f"{B}/informe_ejecutivo.pdf",pagesize=A4,leftMargin=40,rightMargin=40,topMargin=36,bottomMargin=36,title="StreamView Analytics - Informe ejecutivo").build(S)
S2=[Paragraph("StreamView Analytics",T),P("<b>Resumen ejecutivo · EP5 ADY1104</b> · Autor/a: [escribe tu nombre]")]+brief+[im("g1_series_vs_peliculas.png",11)]
SimpleDocTemplate(f"{B}/resumen_ejecutivo.pdf",pagesize=A4,leftMargin=40,rightMargin=40,topMargin=36,bottomMargin=36,title="StreamView Analytics - Resumen ejecutivo").build(S2)
