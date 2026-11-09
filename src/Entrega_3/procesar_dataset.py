from pathlib import Path

import pandas as pd


# Estas rutas se calculan desde este archivo, no desde la carpeta
# que esté abierta en la terminal.
ENTREGA_DIR = Path(__file__).resolve().parent
RUTA_ORIGINAL = ENTREGA_DIR / "datos" / "demo-salaries-original.csv"
RUTA_PREPARADO = ENTREGA_DIR / "datos" / "demo-salaries-preparado.csv"
CARPETA_RESULTADOS = ENTREGA_DIR / "resultados"

# Cargar el CSV original y crear una copia para trabajar.
df_original = pd.read_csv(RUTA_ORIGINAL)
df = df_original.copy()

# Revisar la estructura y la calidad inicial del dataset.
print("Tamaño original:", df_original.shape)
print("\nTipos de columnas:")
print(df_original.dtypes)
print("\nValores nulos por columna:")
print(df_original.isna().sum())
print("\nFilas repetidas después de la primera aparición:")
print(df_original.duplicated().sum())
print("\nPrimeras cinco filas:")
print(df_original.head())

# Verificar que estén las variables necesarias para el análisis.
columnas_requeridas = {
    "work_year",
    "experience_level",
    "employment_type",
    "job_title",
    "salary",
    "salary_currency",
    "salary_in_usd",
    "remote_ratio",
    "company_size",
}

faltantes = columnas_requeridas - set(df.columns)
if faltantes:
    raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")

# Asegurar que estas variables numéricas sean enteros.
columnas_numericas = [
    "work_year",
    "salary",
    "salary_in_usd",
    "remote_ratio",
]

for columna in columnas_numericas:
    df[columna] = pd.to_numeric(df[columna], errors="raise").astype("Int64")

# Reemplazar códigos por etiquetas más claras.
categorias = {
    "experience_level": {
        "EN": "Inicial",
        "MI": "Intermedio",
        "SE": "Senior",
        "EX": "Ejecutivo",
    },
    "employment_type": {
        "FT": "Tiempo completo",
        "PT": "Tiempo parcial",
        "CT": "Contrato",
        "FL": "Freelance",
    },
    "company_size": {
        "S": "Pequeña",
        "M": "Mediana",
        "L": "Grande",
    },
}

for columna, equivalencias in categorias.items():
    valores = df[columna].astype("string").str.strip()
    desconocidos = set(valores.dropna()) - set(equivalencias)

    if desconocidos:
        raise ValueError(
            f"Códigos no contemplados en {columna}: {sorted(desconocidos)}"
        )

    df[columna] = valores.map(equivalencias)

# Crear la modalidad laboral a partir del porcentaje remoto.
modalidades = {
    0: "Presencial",
    50: "Híbrido",
    100: "Remoto",
}

ratios_desconocidos = set(df["remote_ratio"].dropna().astype(int)) - set(modalidades)
if ratios_desconocidos:
    raise ValueError(f"Valores inesperados en remote_ratio: {sorted(ratios_desconocidos)}")

df["remote_work_mode"] = df["remote_ratio"].map(modalidades)

# Revisar que no haya salarios negativos en dólares.
if (df["salary_in_usd"].dropna() < 0).any():
    raise ValueError("Se encontraron salarios negativos en salary_in_usd.")

print("\nTamaño después de transformar:", df.shape)
print("Valores nulos después de transformar:", int(df.isna().sum().sum()))
print("Filas repetidas conservadas:", int(df.duplicated().sum()))
print("\nModalidades creadas:")
print(df["remote_work_mode"].value_counts(dropna=False))
print("\nPrimeras filas transformadas:")
print(df.head())

# Comparar salarios por experiencia, modalidad remota y tamaño de empresa.
tabla_principal = (
    df.groupby(
        [
            "experience_level",
            "remote_work_mode",
            "company_size",
        ],
        dropna=False,
    )
    .agg(
        cantidad_registros=("salary_in_usd", "size"),
        salario_usd_mediana=("salary_in_usd", "median"),
        salario_usd_promedio=("salary_in_usd", "mean"),
        salario_usd_q1=("salary_in_usd", lambda valores: valores.quantile(0.25)),
        salario_usd_q3=("salary_in_usd", lambda valores: valores.quantile(0.75)),
    )
    .reset_index()
    .sort_values(
        ["experience_level", "remote_work_mode", "company_size"]
    )
)

# Comprobar que la tabla cuenta todas las filas del dataset.
total_en_tabla = int(tabla_principal["cantidad_registros"].sum())
if total_en_tabla != len(df):
    raise ValueError(
        f"La tabla cuenta {total_en_tabla} filas, pero el dataset tiene {len(df)}."
    )

print("\nTabla de la pregunta principal:")
print(tabla_principal.to_string(index=False))
print(f"\nCombinaciones de grupos observadas: {len(tabla_principal)}")
print(f"Total de registros contabilizados: {total_en_tabla}")

# Crear la carpeta de resultados si todavía no existe.
CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)

# Guardar el dataset enriquecido y la tabla principal.
df.to_csv(RUTA_PREPARADO, index=False, encoding="utf-8-sig")

ruta_tabla_principal = (
    CARPETA_RESULTADOS / "pregunta_principal_salarios_por_grupo.csv"
)
tabla_principal.to_csv(
    ruta_tabla_principal,
    index=False,
    encoding="utf-8-sig",
)

print(f"\nDataset preparado guardado en: {RUTA_PREPARADO}")
print(f"Tabla principal guardada en: {ruta_tabla_principal}")

# Contar registros por año, experiencia y tipo de empleo.
tabla_apoyo_1 = (
    df.groupby(
        ["work_year", "experience_level", "employment_type"],
        dropna=False,
    )
    .size()
    .reset_index(name="cantidad_registros")
    .sort_values(
        ["work_year", "experience_level", "employment_type"]
    )
)

# Verificar que todas las filas estén contabilizadas.
if int(tabla_apoyo_1["cantidad_registros"].sum()) != len(df):
    raise ValueError("Los conteos de la tabla no coinciden con el total del dataset.")

# Guardar la tabla en formato CSV.
ruta_apoyo_1 = (
    CARPETA_RESULTADOS
    / "pregunta_apoyo_1_registros_por_anio_experiencia_empleo.csv"
)
tabla_apoyo_1.to_csv(ruta_apoyo_1, index=False, encoding="utf-8-sig")

print("\nRegistros por año, experiencia y tipo de empleo:")
print(tabla_apoyo_1.to_string(index=False))
print(f"\nTotal contabilizado: {tabla_apoyo_1['cantidad_registros'].sum()}")
print(f"Tabla guardada en: {ruta_apoyo_1}")

# Calcular cuántos registros hay por cargo y su salario mediano en USD.
tabla_apoyo_2 = (
    df.groupby("job_title", dropna=False)
    .agg(
        cantidad_registros=("salary_in_usd", "size"),
        salario_usd_mediana=("salary_in_usd", "median"),
    )
    .reset_index()
    .sort_values(
        ["cantidad_registros", "job_title"],
        ascending=[False, True],
    )
)

# Verificar que se hayan contabilizado todos los registros.
if int(tabla_apoyo_2["cantidad_registros"].sum()) != len(df):
    raise ValueError("Los conteos por cargo no coinciden con el total del dataset.")

# Guardar la tabla completa; mostrar solo los diez primeros cargos.
ruta_apoyo_2 = (
    CARPETA_RESULTADOS
    / "pregunta_apoyo_2_cargos_por_registros_y_mediana.csv"
)
tabla_apoyo_2.to_csv(ruta_apoyo_2, index=False, encoding="utf-8-sig")

print("\nDiez cargos con más registros:")
print(tabla_apoyo_2.head(10).to_string(index=False))
print(f"\nCargos en la tabla: {len(tabla_apoyo_2)}")
print(f"Total contabilizado: {tabla_apoyo_2['cantidad_registros'].sum()}")
print(f"Tabla guardada en: {ruta_apoyo_2}")

# Resumir registros y salario mediano por año de referencia.
tabla_apoyo_3 = (
    df.groupby("work_year", dropna=False)
    .agg(
        cantidad_registros=("salary_in_usd", "size"),
        salario_usd_mediano=("salary_in_usd", "median"),
    )
    .reset_index()
    .sort_values("work_year").copy()
)

# Calcular el cambio de la mediana respecto al año anterior.
tabla_apoyo_3.loc[:, "variacion_mediana_usd_vs_anio_anterior"] = (
    tabla_apoyo_3["salario_usd_mediano"].diff()
)

tabla_apoyo_3.loc[:, "variacion_mediana_porcentual_vs_anio_anterior"] = (
    tabla_apoyo_3["salario_usd_mediano"].pct_change() * 100
)

# Verificar que se hayan contado todos los registros.
if int(tabla_apoyo_3["cantidad_registros"].sum()) != len(df):
    raise ValueError("Los conteos por año no coinciden con el total del dataset.")

# Guardar la tabla en formato CSV.
ruta_apoyo_3 = (
    CARPETA_RESULTADOS / "pregunta_apoyo_3_salario_mediano_por_anio.csv"
)
tabla_apoyo_3.to_csv(ruta_apoyo_3, index=False, encoding="utf-8-sig")

print("\nSalario mediano por año de referencia:")
print(tabla_apoyo_3.to_string(index=False))
print(f"\nTotal contabilizado: {tabla_apoyo_3['cantidad_registros'].sum()}")
print(f"Tabla guardada en: {ruta_apoyo_3}")

# Crear un resumen del DataFrame preparado.
lineas_reporte = [
    "RESUMEN DEL DATAFRAME PREPARADO",
    "=" * 40,
    f"Filas: {len(df)}",
    f"Columnas: {len(df.columns)}",
    f"Filas repetidas: {int(df.duplicated().sum())}",
    "",
    "Columnas y tipos:",
]

for columna, tipo in df.dtypes.items():
    lineas_reporte.append(f"- {columna}: {tipo}")

lineas_reporte.extend([
    "",
    "Valores nulos por columna:",
])

for columna, cantidad in df.isna().sum().items():
    lineas_reporte.append(f"- {columna}: {cantidad}")

lineas_reporte.extend([
    "",
    "Estadísticas descriptivas de las columnas numéricas:",
    df.describe().round(2).to_string(),
])

texto_reporte = "\n".join(lineas_reporte) + "\n"

ruta_reporte = CARPETA_RESULTADOS / "resumen_dataframe.txt"
ruta_reporte.write_text(texto_reporte, encoding="utf-8")

print(f"\nResumen descriptivo guardado en: {ruta_reporte}")