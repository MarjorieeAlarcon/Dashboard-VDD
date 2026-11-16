# StreamView Analytics – EP5 (ADY1104 Visualización de Datos)

Dashboard interactivo, informe ejecutivo y análisis reproducible sobre 32.000 títulos (2010–2025).

## Estructura
- `data/` – CSV originales (películas y series).
- `src/analisis.py` – calcula todas las cifras y las guarda en `src/results.json`.
- `src/informe.py` – genera los gráficos de `images/` y los PDF.
- `notebooks/EDA_EA3.ipynb` – ejecuta el análisis paso a paso.
- `dashboard/dashboard_streamview.html` – dashboard (abrir en el navegador, sin internet).
- `informe_ejecutivo.pdf` y `resumen_ejecutivo.pdf` – entregables.

## Reproducir
```
pip install pandas numpy matplotlib reportlab pillow
python src/analisis.py
python src/informe.py
```

## Notas de datos
- Visualizaciones = `popularity` × 1000 (suma 1.363,8 millones).
- El rating excluye los 4.572 títulos con `rating = 0`.
- Ingresos y presupuesto: solo 5.645 películas. La duración de películas no viene en el dataset.
- Los pósters del dashboard son ilustraciones; cada uno permite subir una foto propia.
