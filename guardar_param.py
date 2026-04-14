import json

ARCHIVO = "param_n_volat"


def actualizar_parametro(clave, valor):
    try:
        with open(ARCHIVO, "r") as f:
            params = json.load(f)
    except OSError:
        params = {"setpoint": 25.0, "periodo": 10, "modo": "MANUAL", "rele": "False"}

    params[clave] = valor

    with open(ARCHIVO, "w") as f:
        json.dump(params, f)

def leer_params():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except OSError:
        print("No se detectó el archivo, se crearán valores por defecto.")
        params = {"setpoint": 25.0, "periodo": 10, "modo": "MANUAL", "rele": False}
        with open(ARCHIVO, "w") as f:
            json.dump(params, f)
        return params
