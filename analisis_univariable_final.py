import pandas as pd 
import os 
import matplotlib.pyplot as plt 
import seaborn as sns 
from tkinter import filedialog, Tk  # Librerías para el selector de archivos

# --- 1. CONFIGURACIÓN DEL SELECTOR DE ARCHIVOS ---
root = Tk()
root.withdraw()  # Ocultamos la ventana principal de tkinter
root.attributes('-topmost', True)  # Forzamos a que la ventana salga al frente

print("--- SELECCIONE EL ARCHIVO EXCEL PARA PROCESAR ---")
nombre_archivo = filedialog.askopenfilename(
    title="Seleccionar archivo de Migración",
    filetypes=[("Archivos de Excel", "*.xlsx *.xls")]
)

# --- 2. CONFIGURACIÓN DE SALIDA ---
carpeta_salida = 'graficos_tranvia2' 

if not nombre_archivo:
    print(" ERROR: No se seleccionó ningún archivo. Saliendo...")
else:
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    print(f"--- INICIANDO PROCESAMIENTO: {os.path.basename(nombre_archivo)} ---")

    try:
        # --- 3. CARGA Y RENOMBRADO DE DATOS ---
        df = pd.read_excel(nombre_archivo)
        
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
        print(" Columnas renombradas y datos cargados.\n")

        # --- 4. VARIABLES Y CONFIGURACIÓN ---
        variables_todas = [
            'Estacion', 'Zona_de_residencia', 'Zona_de_destino', 'Nivel_de_instruccion',
            'Edad', 'Sexo', 'Ingresos', 'Frecuencia_de_uso', 'Transporte_anterior',
            'Factor_de_cambio', 'Satisfaccion', 'Motivo_de_viaje', 'Bus_anterior', 'Sugerencia'
        ]

        config_graficos = {
            'Estacion': 'horizontal',
            'Sexo': 'pastel',
            'Edad': 'vertical',
            'Nivel_de_instruccion': 'vertical',
            'Ingresos': 'vertical',
            'Frecuencia_de_uso': 'vertical',
            'Transporte_anterior': 'horizontal',
            'Factor_de_cambio': 'vertical',
            'Satisfaccion': 'pastel',
            'Motivo_de_viaje': 'horizontal'
        }

        # --- 5. BUCLE DE PROCESAMIENTO ---
        for i, var in enumerate(variables_todas, 1):
            if var in df.columns:
                datos_var = df[var].dropna()
                total_n = len(datos_var)
                if total_n == 0: continue 

                f_abs = datos_var.value_counts()
                f_rel = (f_abs / total_n) * 100
                f_abs_acum = f_abs.cumsum()
                f_rel_acum = f_rel.cumsum()

                tabla = pd.DataFrame({
                    'ni': f_abs.values,
                    'fi%': f_rel.map('{:.1f}%'.format).values,
                    'Ni': f_abs_acum.values,
                    'Fi%': f_rel_acum.map('{:.1f}%'.format).values
                }, index=f_abs.index)

                print(f"\nVARIABLE {i}: {var}")
                print("-" * 50)
                print(tabla)
                print(f"\nModa = {f_abs.index[0]} ({f_abs.values[0]}, {f_rel.values[0]:.1f}%)")

                # --- 6. GENERACIÓN DE GRÁFICOS ---
                if var in config_graficos:
                    tipo_grafico = config_graficos[var]
                    plt.figure(figsize=(12, 7))
                    sns.set_style("white")
                    
                    etiquetas_texto = [f'{n} ({p:.1f}%)' for n, p in zip(f_abs.values, f_rel.values)]

                    if tipo_grafico == 'horizontal':
                        ax = sns.barplot(x=f_abs.values, y=f_abs.index, hue=f_abs.index, palette='viridis', legend=False)
                        for idx, (valor, texto) in enumerate(zip(f_abs.values, etiquetas_texto)):
                            ax.text(valor + (max(f_abs.values)*0.01), idx, texto, va='center', fontweight='bold')
                        plt.xlabel('Frecuencia Absoluta (ni)')

                    elif tipo_grafico == 'vertical':
                        ax = sns.barplot(x=f_abs.index, y=f_abs.values, hue=f_abs.index, palette='magma', legend=False)
                        for idx, (valor, texto) in enumerate(zip(f_abs.values, etiquetas_texto)):
                            ax.text(idx, valor + (max(f_abs.values)*0.02), texto, ha='center', fontweight='bold')
                        plt.xticks(rotation=30, ha='right')
                        plt.ylabel('Frecuencia Absoluta (ni)')

                    elif tipo_grafico == 'pastel':
                        plt.pie(f_abs, labels=f_abs.index, autopct='%1.1f%%', startangle=140, 
                                colors=sns.color_palette("Set3"), wedgeprops={'edgecolor': 'white'})
                    
                    plt.title(f'Distribución: {var}', fontsize=14, fontweight='bold', pad=20)
                    plt.tight_layout()
                    
                    plt.savefig(f'{carpeta_salida}/{var}.png', dpi=300)
                    plt.close()
                    print(f" Gráfico guardado en: {carpeta_salida}/{var}.png")

                print("=" * 60)
            else:
                print(f" Variable '{var}' no encontrada en el DataFrame.")

        print(f"\n PROCESO FINALIZADO CON ÉXITO.")

    except Exception as e:
        print(f" Ocurrió un error inesperado: {e}")