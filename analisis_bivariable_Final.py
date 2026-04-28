import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency, spearmanr
from tkinter import filedialog, Tk  # Librerías para el selector

# --- 1. CONFIGURACIÓN DEL SELECTOR DE ARCHIVOS ---
root = Tk()
root.withdraw()
root.attributes('-topmost', True)

print("--- SELECCIONE EL ARCHIVO EXCEL PARA EL ANÁLISIS BIVARIABLE ---")
archivo_seleccionado = filedialog.askopenfilename(
    title="Seleccionar archivo de Migración",
    filetypes=[("Archivos de Excel", "*.xlsx *.xls")]
)

# --- 2. CONFIGURACIÓN INICIAL Y CARGA ---
carpeta_graficos = 'graficos_bivariable_final'

if not archivo_seleccionado:
    print("❌ ERROR: No se seleccionó ningún archivo. Saliendo...")
    exit()

if not os.path.exists(carpeta_graficos):
    os.makedirs(carpeta_graficos)

try:
    # --- CARGAR DATOS ---
    df = pd.read_excel(archivo_seleccionado)
    
    # --- RENOMBRAR VARIABLES (Mapeo de nombres largos a cortos) ---
    mapeo_columnas = {
        '1. Estación del tranvía en la cual se levanta la información': 'Estacion',
        '2. ¿En qué zona de la ciudad se encuentra su lugar de residencia?': 'Zona_de_residencia',
        '3. ¿En qué zona de la ciudad se encuentra su destino de viaje?': 'Zona_de_destino',
        '4. ¿Cuál es el Nivel de instrucción del encuestado?': 'Nivel_de_instruccion',
        '6. Edad': 'Edad',
        '6. Sexo al nacer': 'Sexo',
        '7. Ingresos': 'Ingresos',
        '8. ¿Con qué frecuencia utiliza el tranvía para sus desplazamientos habituales?': 'Frecuencia_de_uso',
        '9. ¿Cuál fue el motivo principal de su viaje?': 'Motivo_de_viaje',
        '10. ¿Qué medio de transporte utilizaba antes de usar el tranvía?': 'Transporte_anterior',
        '11. ¿Cuál es el factor principal que le motivó a cambiar al tranvía como medio de transporte?': 'Factor_de_cambio',
        '12. ¿Qué grado de satisfacción tiene con el servicio del tranvía?': 'Satisfaccion',
        'Qué línea de bus utilizaba?': 'Bus_anterior',
        '13. ¿Cuál sería su sugerencia para mejorar el servicio?': 'Sugerencia'
    }
    df = df.rename(columns=mapeo_columnas)
    print(f"✅ Datos de '{os.path.basename(archivo_seleccionado)}' cargados y renombrados.\n")

except Exception as e:
    print(f"❌ Error al procesar el archivo: {e}")
    exit()

# --- 3. MAPEOS DE ESCALAS (Basados en los nuevos nombres) ---
mapas_ordinales = {
    'Edad': {
        '6 - 11 años': 1, '12 - 17 años': 2, '18 - 24 años': 3, 
        '25 - 64 años': 4, '65 años en adelante': 5
    },
    'Nivel_de_instruccion': {
        'Ninguno': 1, 'Básica': 2, 'Bachillerato': 3, 
        'Tercer Nivel (Universidad, Tecnológico)': 4, 
        'Cuarto Nivel (Maestría, Doctorado, Posgrado)': 5
    },
    'Frecuencia_de_uso': {
        'Todos los días': 4, 'Entre 3 y 5 veces por semana': 3, 
        'Entre 1 y 2 veces por semana': 2, 'Menos de una vez a la semana': 1
    },
    'Satisfaccion': {
        'Muy satisfecho': 3, 'Satisfecho': 2, 'Ni satisfecho ni insatisfecho': 1
    }
}

# --- 4. CONFIGURACIÓN DE CRUCES ---
cruces_config = [
    ('Sexo', 'Satisfaccion', 'agrupadas', False),
    ('Edad', 'Frecuencia_de_uso', 'apiladas_100', True), 
    ('Ingresos', 'Transporte_anterior', 'agrupadas', False),
    ('Motivo_de_viaje', 'Frecuencia_de_uso', 'apiladas_100', False),
    ('Nivel_de_instruccion', 'Satisfaccion', 'apiladas_100', True), 
    ('Edad', 'Factor_de_cambio', 'horizontales', False),
    ('Ingresos', 'Factor_de_cambio', 'horizontales', False),
    ('Estacion', 'Motivo_de_viaje', 'agrupadas', False)
]

# (El resto de la función analizar_cruce_completo y el bucle final se mantienen igual...)

def analizar_cruce_completo(v1, v2, tipo_grafico, calcular_spearman):
    if v1 not in df.columns or v2 not in df.columns:
        return

    # Limpieza de nulos
    temp_df = df[[v1, v2]].dropna()
    n_total = len(temp_df)

    # --- TABLAS (Paso 1) ---
    ct_abs_margen = pd.crosstab(temp_df[v1], temp_df[v2], margins=True, margins_name="TOTAL")
    ct_pct = pd.crosstab(temp_df[v1], temp_df[v2], normalize='index') * 100

    # --- ESTADÍSTICOS CHI-CUADRADO Y V DE CRAMÉR (Paso 3 y 4) ---
    ct_test = pd.crosstab(temp_df[v1], temp_df[v2])
    chi2, p, dof, expected = chi2_contingency(ct_test)
    v_cramer = np.sqrt(chi2 / (n_total * (min(ct_test.shape) - 1)))

    # --- MOSTRAR EN CONSOLA ---
    print(f"\n>>> ANÁLISIS BIVARIABLE: {v1} vs {v2}")
    print("-" * 75)
    print("TABLA DE CONTINGENCIA (Absolutas):")
    print(ct_abs_margen)
    print(f"\nESTADÍSTICOS DE ASOCIACIÓN:")
    print(f"χ² = {chi2:.3f} | p-valor = {p:.4f} | V de Cramér = {v_cramer:.3f}")
    
    # --- PASO 5: SPEARMAN (Corregido con escalas numéricas) ---
    if calcular_spearman:
        # Mapeamos los textos a los números de tu escala
        s1 = temp_df[v1].map(mapas_ordinales.get(v1, {}))
        s2 = temp_df[v2].map(mapas_ordinales.get(v2, {}))
        
        rho, p_spearman = spearmanr(s1, s2, nan_policy='omit')
        print(f"\nCORRELACIÓN DE SPEARMAN (Basada en rangos numéricos):")
        print(f"Rho de Spearman (ρ) = {rho:.3f} | p-valor = {p_spearman:.4f}")
        
        interp = "Fuerte" if abs(rho) > 0.7 else "Moderada" if abs(rho) > 0.3 else "Débil"
        print(f"Interpretación: Correlación {interp} ({'Positiva' if rho > 0 else 'Negativa'})")

    print("-" * 75)

    # --- GENERAR GRÁFICO EN PORCENTAJE (Paso 2) ---
    plt.figure(figsize=(12, 7))
    sns.set_style("white")

    if tipo_grafico == 'agrupadas':
        ax = ct_pct.plot(kind='bar', figsize=(12, 7), width=0.8, edgecolor='white')
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%', padding=3, fontweight='bold', fontsize=9)
        plt.ylabel('Porcentaje (%)')

    elif tipo_grafico == 'apiladas_100':
        ax = ct_pct.plot(kind='bar', stacked=True, figsize=(12, 7), colormap='viridis', edgecolor='white')
        for container in ax.containers:
            labels = [f'{v:.1f}%' if v > 4 else '' for v in container.datavalues]
            ax.bar_label(container, labels=labels, label_type='center', color='white', fontweight='bold')
        plt.ylabel('Distribución Porcentual (%)')

    elif tipo_grafico == 'horizontales':
        ax = ct_pct.plot(kind='barh', figsize=(12, 8), width=0.8, edgecolor='white')
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%', padding=3, fontweight='bold', fontsize=9)
        plt.xlabel('Porcentaje (%)')

    plt.title(f'Relación Porcentual: {v1} vs {v2}', fontsize=14, fontweight='bold', pad=20)
    plt.legend(title=v2, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    if tipo_grafico != 'horizontales': plt.ylim(0, 115) 

    plt.tight_layout()
    nombre_grafico = f"BIV_FINAL_{v1}_vs_{v2}.png".replace(" ", "_")
    plt.savefig(os.path.join(carpeta_graficos, nombre_grafico), dpi=300)
    plt.close('all')
    print(f"📊 Gráfico guardado: {nombre_grafico}\n" + "="*75)

# --- EJECUCIÓN ---
for var1, var2, tipo, spearman_on in cruces_config:
    analizar_cruce_completo(var1, var2, tipo, spearman_on)

print(f"\n🚀 PROCESO FINALIZADO. Gráficos en la carpeta: '{carpeta_graficos}'")