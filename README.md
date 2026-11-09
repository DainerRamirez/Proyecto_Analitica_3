# Proyecto_analitica_3

## Entrega AE3: preparación y análisis de salarios

### Preguntas abordadas

- ¿Cómo se comparan los salarios en USD por experiencia, modalidad de trabajo y tamaño de empresa?
- ¿Cuántos registros hay por año de referencia, experiencia y tipo de empleo?
- ¿Qué cargos tienen más registros y cuál es su salario mediano?
- ¿Cómo cambia la mediana salarial entre los años disponibles?

### Transformaciones y controles

Se conservaron las 3.755 filas del dataset original y se creó un DataFrame preparado de 12 columnas. Se cambiaron los códigos de experiencia, tipo de empleo y tamaño de empresa por etiquetas legibles, y se agregó `remote_work_mode` a partir de `remote_ratio`: 0 = presencial, 50 = híbrido y 100 = remoto.

No se encontraron valores nulos. Se conservaron las 1.171 filas repetidas porque no hay un identificador para determinar si son errores o registros distintos con valores iguales. Las comparaciones salariales usan `salary_in_usd`. Se usa `work_year` como año de referencia porque el dataset no proporciona una fecha exacta de pago.

### Archivos generados

- Notebook ejecutado: `src/Entrega_3/Semana_3_AE3.ipynb`
- Script de procesamiento: `src/Entrega_3/procesar_dataset.py`
- Dataset original: `src/Entrega_3/datos/demo-salaries-original.csv`
- Dataset preparado: `src/Entrega_3/datos/demo-salaries-preparado.csv`
- Resultados CSV y resumen descriptivo: `src/Entrega_3/resultados/`

El notebook genera el dataset preparado, cuatro tablas CSV y `resumen_dataframe.txt`. Las tablas contienen conteos por combinación o cargo y estadísticas salariales para responder las preguntas.

### Ejecución

Desde la raíz del proyecto, ejecuta el script:

```bash
python src/Entrega_3/procesar_dataset.py