import json
from collections import defaultdict
import matplotlib.pyplot as plt

#CANASASTA HOSPITALARIA DEFINIDA:

# canasta = {
#     "Shampoo suave" : {},
#     "Jabón" : {},
#     "Pasta dental": {},
#     "Toallitas húmedas": {},
#     "Pañales": {},
#     "Crema protectora": {},
#     "Compotas": {},
#     "Jugos": {},
#     "Galletas dulces Oreo": {},
#     "Agua Embotellada" :{}
# }


def cargar_json(ruta):
    """Funcion para cargar los datos de las mipymes json"""
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    return datos['mipymes'], datos['tasa_cambio_semana']

def peso_minimo_por_producto(mipymes):
    """
    Devuelve un diccionario con el peso minimo observado por nombre de producto
    """
    
    pesos = defaultdict(list) # agrupa todos los pesos netos observados por nombre de producto
    
    for mipyme in mipymes:
        for p in mipyme['productos_hospitalarios']:
            if p['peso_neto']:
                clave = p['nombre'].lower().strip()
                pesos[clave].append(p['peso_neto'])
    return {k: min(v) for k, v in pesos.items()} # usamos min oara encontrar el peso mas pequenio de cada producto
    #esto nos permite estandarizar precios con vase en la presentacion mas pequena real

def precio_estandarizado(producto, peso_minimo):
    """
    Convierte el precio a CUP por unidad minima observada del producto.
    """    
    nombre = producto["nombre"].lower().strip()
    if producto["peso_neto"] and producto["unidad"] in ["ml", "g"]:
        factor = producto["peso_neto"] / peso_minimo.get(nombre, producto["peso_neto"])
        return producto["precio_cup"] / factor
    else:
        return producto["precio_cup"]

def promedio_estandarizado_por_producto(mipyme, peso_minimo):
    agrupados = defaultdict(list)
    for p in mipyme["productos_hospitalarios"]:
        clave = p["nombre"].lower().strip()
        precio = precio_estandarizado(p, peso_minimo)
        agrupados[clave].append(precio)
    
    return {k: sum(v)/ len(v) for k, v in agrupados.items()}

def costo_canasta_estandarizada(mipyme, peso_minimo):
    promedios = promedio_estandarizado_por_producto(mipyme, peso_minimo)
    return  round(sum(promedios.values()), 2)

def porcentaje_salario(costo, salario= 5000):
    """
    Calcula que porcentaje del salario estatal representa el costo total de una canasta.
    
    Parametros:
    - Costo (float): el costo total en CUP de la canasta hospitalaria.
    - Salario (float): el salario estatal  mensual en CUP (por defecto: 5000)
    
    Retorna:
    float : porcentaje del salario consumido, redondeado a dos decimales
    """
    
    if salario == 0:
        return None # evitar ZERODIVISION ERROR
    return round((costo / salario) * 100, 2)

def clasificar_mipyme_por_distancia(mipyme, umbral= 0.5):
    """Clasifica una mipyme como cercana o lejana segun su distancia al hospital"""
    return "cercana" if mipyme["distancia_al_hospital_km"] <= umbral else "lejana"

def variedad_por_grupo(mipymes, canasta):
    """ 
    Cuenta cuantos productos de la canasta estan disponibles por grupo de distancia
    """
    grupos = {"cercana": set(), "lejana": set()}
    nombres_canasta = set(k.lower() for k in canasta.keys())
    
    for mipyme in mipymes:
        grupo = clasificar_mipyme_por_distancia(mipyme)
        for p in mipyme["productos_hospitalarios"]:
            nombre = p["nombre"].lower().strip()
            if nombre in nombres_canasta:
                grupos[grupo].add(nombre)
    return {k : len(v) for k, v in grupos.items}

def cobertura_por_producto(mipymes, canasta):
    """ 
        Para cada producto de la canasta, indica si aparece en mipymes cercanas, lejanas o ambas
    """
    
    cobertura = defaultdict(set)
    nombres_canasta = set(k.lower() for k in canasta.keys())

    for mipyme in mipymes:
        grupo = clasificar_mipyme_por_distancia(mipyme)
        for p in mipyme["productos_hospitalarios"]:
            nombre = p["nombre"].lower().strip()
            if nombre in nombres_canasta:
                cobertura[nombre].add(grupo)
    return {k: sorted(list(v)) for k , v in cobertura.items()}

def costo_canasta_semanal_promedio( mipymes, peso_minimo, canasta):
    """ 
    Calcula el costo total de la canasta  semanal infantil usando precios promedio estandarizados por producto en
    todas las mipymes, multiplicando por la cantidad semanal definida
    """
    
    precios = defaultdict(list)
    
    for mipyme in mipymes:
        for p in mipyme["productos_hospitalarios"]:
            nombre = p["nombre"].lower().strip()
            if nombre in [k.lower() for k in canasta.keys()]:
                #Estandarizar por peso minimo observado
                if p["peso_neto"] and p["unidad"] in ["ml", "g"]:
                    factor = p["peso_neto"] / peso_minimo.get(nombre, p["peso_neto"])
                    precio = p["precio_cup"] / factor
                    
                else:
                    precio = p["precio_cup"]
                precios[nombre].append(precio)
    total = 0
    
    for nombre_canasta, info  in canasta.items():
        nombre = nombre_canasta.lower()
        cantidad = info["cantidad"]
        
        if nombre in precios and precios[nombre]:
            promedio = sum(precios[nombre]) / len(precios[nombre])
            total += promedio * cantidad
    return round(total, 2)

#VISUALIZACION 
def visuzalizar_canasta_vs_salario(costo_canasta, salario_estatal = 5000):
    """ 
    Genera una visualizacion  de barras  que compara el salario estatal mensual con el costo semanal de la canasta
    infantil hospitalaria
    Parametros:
    -costo_canasta (float): costo total semanal de la canasta infantil
    - salario_estatal (float): salario mensual de referencia (por defecto: 5000 CUP)
    """
    etiquetas = ["Salario estatal", "Canasta infantil"]
    valores= [salario_estatal, costo_canasta]
    colores = ['#4CAF50', "#F44336"] # verde para el salario, rojo para la canasta
    
    plt.figure(figsize=(8,6))
    barras = plt.bar(etiquetas, valores, color=colores)
    
    #Linea Horizontal de referencia
    plt.axhline(salario_estatal, color = 'gray', linestyle='--', linewidth=1)
    plt.text(1.05, salario_estatal + 100, "Salario estatal", color = 'gray')
    
    #Etiqueta encima de cada barra
    for barra in barras:
        altura = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2, altura +200, f"{int(altura)}CUP", ha = "center", fontsize =10)
    # TITULO y ejes
        plt.title("Costo semanal de la canasta infantil vs salario estatal")
        plt.ylabel("CUP")
        plt.ylim(0, max(valores) + 1500)
    