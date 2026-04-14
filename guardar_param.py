import json

ARCHIVO = "param_n_volat"

# Guardar
#def guardar_params(params):
#    with open(ARCHIVO, "w") as f:
#        json.dump(params, f)

def actualizar_parametro(clave, valor):
    # 1. Leer los datos actuales
    try:
        with open(ARCHIVO, "r") as f:
            params = json.load(f)
    except OSError:
        # Si el archivo no existe todavía, creamos un diccionario base
        # Esto evita que el programa se rompa la primera vez que lo corrés
        print("Da error al leer el archivo, se crearán valores por defecto.")
        params = {"setpoint": 25.0, "periodo": 10, "modo": "AUTO", "rele": "False"}

    # 2. Actualizar solo el valor que nos interesa
    params[clave] = valor

    # 3. Sobrescribir el archivo con el diccionario actualizado
    with open(ARCHIVO, "w") as f:
        json.dump(params, f)

# Leer
def leer_params():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except OSError:
        # Primera vez, retorna valores por defecto
        print("Da error al leer el archivo, se crearán valores por defecto.")
        return {"setpoint": 25.0, "periodo": 500, "modo": "AUTO", "rele": "False"}

# Uso
#params = leer_params()
#print(params["setpoint"])   # → 75.0

#params["setpoint"] = 80.0
#guardar_params(params)