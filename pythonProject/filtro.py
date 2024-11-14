import pandas as pd
import os
import types

# Ruta relativa al archivo dentro de la carpeta "data"
base_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta donde está `filtro.py`
ruta_archivo_excel = os.path.join(base_dir, "data", "filtered3.xlsx")

# Verificar si el archivo existe
if not os.path.exists(ruta_archivo_excel):
    raise FileNotFoundError(f"El archivo '{ruta_archivo_excel}' no se encuentra en la carpeta 'data'.")

# Leer el archivo Excel
df = pd.read_excel(ruta_archivo_excel)

# Validar que las columnas necesarias existan
columna_precio = "Price in (1M Tokens)"
columna_empresa = "Organization"
columna_modelo = "Model"

for columna in [columna_precio, columna_empresa, columna_modelo]:
    if columna not in df.columns:
        raise KeyError(f"La columna '{columna}' no existe en el archivo Excel.")

# Limpiar la columna `Price in (1M Tokens)` y convertir valores a numéricos
df[columna_precio] = pd.to_numeric(df[columna_precio], errors="coerce").fillna(0)

# Crear dinámicamente un método para cada modelo LLM
def metodo_llm_factory(precio, modelo):
    def metodo_llm(self):
        """
        Método dinámico que devuelve los tokens asociados al modelo.
        """
        return f"Modelo: {modelo}, Tokens asociados: {precio}"
    return metodo_llm

# Crear clases dinámicas con nombres reales de las empresas
clases_por_empresa = {}

for index, fila in df.iterrows():
    empresa = fila[columna_empresa]  # Nombre de la empresa
    modelo_llm = fila[columna_modelo]  # Nombre del modelo
    precio = fila[columna_precio]  # Tokens (precio) asociado

    # Verificar si la empresa ya tiene una clase generada
    if empresa not in clases_por_empresa:
        # Crear una nueva clase para la empresa
        class Empresa:
            def __init__(self, nombre):
                self.nombre = nombre

        Empresa.__name__ = empresa
        clases_por_empresa[empresa] = Empresa(empresa)

    # Crear el método dinámico para el modelo
    nombre_metodo = ''.join([palabra.capitalize() for palabra in modelo_llm.split('_')])
    metodo = metodo_llm_factory(precio, modelo_llm)
    setattr(clases_por_empresa[empresa], nombre_metodo, types.MethodType(metodo, clases_por_empresa[empresa]))

# Iterar sobre las clases dinámicas y mostrar los tokens asociados a cada modelo
for empresa, instancia in clases_por_empresa.items():
    print(f"\nEmpresa: {empresa}")
    for metodo in dir(instancia):
        if not metodo.startswith("__") and callable(getattr(instancia, metodo)):  # Ignorar métodos internos
            metodo_func = getattr(instancia, metodo)
            print(f"Resultado del método {metodo}: {metodo_func()}")
