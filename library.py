import json
from collections import defaultdict
import matplotlib.pyplot as plt

def cargar_archivos(ruta):

    with open(ruta, 'r', encoding='utf-8') as file:
        return json.load(file)   
    
# =============================================================================
# FUNCIONES DE CLASIFICACIÓN Y CÁLCULO DE PESOS
# =============================================================================


def clasificar_tipo_producto(producto):
    """
    Clasifica productos según cómo deben ser estandarizados
    """
    # Productos que se venden por UNIDADES (no necesitan estandarización por peso)
    productos_unitarios = {
        'pañales', 'limpieza', 'huevos'  # toallitas, pañales, huevos por unidad
    }
    
    # Productos que se venden por PESO/VOLUMEN (necesitan estandarización)
    productos_pesables = {
        'compotas', 'mermeladas', 'jugos', 'carnes', 'leguminosas', 
        'capilar', 'corporal', 'cuidados', 'cereales'
    }
    
    categoria = producto['category']
    
    if categoria in productos_unitarios:
        return 'unitario'
    elif categoria in productos_pesables:
        return 'pesable'
    else:
        return 'unitario'  # Por defecto

def peso_minimo_por_producto(mipymes):
    """
    Calcula el peso minimo observado de cada producto en mipymes
    devolviendo un diccionario con el peso minimo por categorias

    args:
        mipymes (list): lista de todas las mipymes
    returns:
        dict {category : peso_minimo}
    """
    
    min_weight_per_category = defaultdict(list)
        
    for mipyme in mipymes:
        for product in mipyme['products']:
            if product['net_weight'] == None:
                category= product['category'].lower().strip()
                min_weight_per_category[category].append(-1)
            if product['net_weight']:
                category = product['category'].lower().strip()
                min_weight_per_category[category].append(product['net_weight'])
                
    return {k: min(v) for k, v in min_weight_per_category.items()}
             
def estandarizar_precio_producto(producto, peso_minimo_por_categoria):
    """
        Convierte el precio a CUP por unidad minima observada del producto si el producto es "pesable"
        si es "unitario" el precio del producto ya esta estandarizado 

    Args:
        producto (dict): diccionario que contiene toda la info del producto  
        peso_minimo_categoria (dict):  contiene el peso minimo observado de todas las categorias de los productos
    Returns:
        precio estandarizado
    """
    categoria = producto['category']
    tipo = clasificar_tipo_producto(producto)
    
    
    if tipo == "unitario":
        return producto['price_cup']  #para productos unitarios el precio ya esta estandarizado
    

    elif tipo == 'pesable':
        # Para productos pesables, estandarizar por peso mínimo
        if (producto.get('net_weight') and 
            producto['unit'] in ['g', 'ml'] and
            categoria in peso_minimo_por_categoria):
            
            peso_min = peso_minimo_por_categoria[categoria]
            factor = producto['net_weight'] / peso_min
            return producto['price_cup'] / factor
        else:
            return producto['price_cup']
    
    else:
        return producto['price_cup'] 
    

# =============================================================================
# FUNCIONES DE CÁLCULO DE COSTOS
# =============================================================================

    
def costo_canasta_semanal_completo(mipymes, canasta, peso_minimo_por_categoria):
    """Calcula el costo promedio semanal de la canasta

    Args:
        mipymes (list): lista de la muestra de mipymes
        canasta (dict): diccionario con la info de las categorias de productos que se necesitan para mantener 
        en buenas condiciones de nutrición e higiene a un niño entre 12 a 24 meses de nacido en el hospital
        peso_minimo_por_categoria (dict): contiene el peso minimo observado de todas las categorias de los productos "pesables"

    Returns:
        _type_: _description_
    """
    precios_estandarizados = defaultdict(list)

    
    # Esta primera parte estandariza  el precio de todos los productos de las mipymes
    # y almacena en un diccionario los precios estandarizados por categorias
    # de esta forma:
    #{ 
    #   "categoria" : [precios_estandarizados_todas_las_mipymes]    
    #}
    for mipyme in mipymes:
        for producto in mipyme['products']:
            categoria = producto['category']
            
            if categoria in canasta:
                precio_estandarizado = estandarizar_precio_producto(
                    producto, peso_minimo_por_categoria
                )
                
                precios_estandarizados[categoria].append(precio_estandarizado)

    total = 0
    
    #Promedia los precios estandarizados de todas las categorias de productos  y multiplica por la cantidad necesaria 
    # de ese producto en una semana ... y el precio total de la canasta en las mipymes es la sumatoria de todos esos
    # productos 
    
    for categoria, info in canasta.items():
        cantidad_semanal = info['cantidad']

        if categoria in precios_estandarizados and precios_estandarizados[categoria]:
            precio_promedio = sum(precios_estandarizados[categoria]) / len(precios_estandarizados[categoria])
            total += precio_promedio * cantidad_semanal

    return round(total, 2)

def costo_promedio_por_producto(mipymes, canasta):
    
    precios_por_categoria = defaultdict(list)
    
    pesos_minimos= peso_minimo_por_producto(mipymes)
    
    for mipyme in mipymes:
        for producto in mipyme['products']:
            categoria = producto['category']
            print(categoria)
            if categoria in canasta:
                precio_estandar = estandarizar_precio_producto(producto, pesos_minimos)
                precios_por_categoria[categoria].append(precio_estandar)
           
    #print(f"{precios_por_categoria}") TEST DE QUE PINCHA :')
    promedio_por_categoria = defaultdict(list)
    for categoria, lista_precios in precios_por_categoria.items():
        promedio_por_categoria[categoria] = sum(lista_precios) / len(lista_precios)
    
    return promedio_por_categoria
    

# =============================================================================
# FUNCIONES DE VISUALIZACIÓN
# =============================================================================

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

def visualizar_proporciones_minima(precios_promedio, canasta, costo_total):
    """
    Grafico circular de la distribucion del costo por categoria de producto
    """
    # Calcular costos y porcentajes
    costos_por_categoria = {}
    for categoria, precio_promedio in precios_promedio.items():
        if categoria in canasta:
            cantidad = canasta[categoria]['cantidad']
            costos_por_categoria[categoria] = precio_promedio * cantidad
    
    # Ordenar
    categorias_ordenadas = sorted(costos_por_categoria.keys(), 
                                key=lambda x: costos_por_categoria[x], 
                                reverse=True)
    
    porcentajes = []
    for categoria in categorias_ordenadas:
        porcentaje = (costos_por_categoria[categoria] / costo_total) * 100
        porcentajes.append(porcentaje)
    
    # Gráfico simple
    plt.figure(figsize=(10, 8))
    plt.pie(porcentajes, labels=[cat.title() for cat in categorias_ordenadas], autopct='%1.1f%%')
    plt.title('Distribución del Costo por Categoría\nCanasta Semanal', fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()