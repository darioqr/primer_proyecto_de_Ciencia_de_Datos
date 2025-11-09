import json

# Reglas de estandarización
REGLAS = {
    "galleticas_dulces": {"unidad_ref": 200, "tipo": "gramos"},
    "galletas_saladas" : {"unidad_ref": 200, "tipo": "gramos"},
    "pastas_bocaditos": {"unidad_ref": 200, "tipo": "ml"},
    "agua_embotellada": {"unidad_ref": 1000, "tipo": "ml"},
    "yogur": {"unidad_ref": 200, "tipo": "ml"},
    "jugo_nectar_fruta": {"unidad_ref": 200, "tipo": "ml"},
    "salsa_mayonesa": {"unidad_ref": 200, "tipo": "ml"},
    "compotas": {"unidad_ref": 200, "tipo": "ml"},
    "papel_sanitario": {"unidad_ref": 1, "tipo": "rollos"},
    "culeros_desechables": {"unidad_ref": 1, "tipo": "unidades"},
    "jabon": {"unidad_ref": 100, "tipo": "gramos"},
    "shampoo": {"unidad_ref": 200, "tipo": "ml"},
    "crema_bebe": {"unidad_ref": 100, "tipo": "ml"},
    "pasta_dientes": {"unidad_ref": 100, "tipo": "ml"},
    "gelatina": {"unidad_ref": 100, "tipo": "gramos"},
    "toallas_humedas": {"unidad_ref": 50, "tipo": "unidades"}
}

#---- Normalizar producto ----

def normalizar_producto(producto):
    nombre = producto["nombre"]
    if nombre not in REGLAS:
        return producto 

    regla = REGLAS[nombre]
    unidad_ref = regla["unidad_ref"]

    peso = producto.get("peso_neto")
    precio = producto.get("precio")

    # precio por unidad de referencia
    precio_estandarizado = (precio / peso) * unidad_ref

    producto["precio_estandarizado"] = round(precio_estandarizado, 2)
    producto["unidad_ref"] = f"{unidad_ref} {regla['tipo']}"
    return producto

def estandarizar_todos(datos_json):
    productos_normalizados = []
    for mipyme in datos_json["mimpymes"]:
        for producto in mipyme["productos"]:
            normalizado = normalizar_producto(producto.copy())
            normalizado["mipyme_id"] = mipyme["id"]
            productos_normalizados.append(normalizado)
    return productos_normalizados

    

# --- CARGA ---
def cargar_json(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)
    

