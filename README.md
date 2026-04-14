# Termostato IoT — Raspberry Pi Pico W

## ¿Qué hace el sistema?

Es un **termostato IoT** programado en MicroPython con `asyncio` y comunicación MQTTS. Tiene 5 tareas corriendo en paralelo:

| Tarea | Descripción |
|---|---|
| `up` | Se re-suscribe a todos los tópicos al reconectarse al broker |
| `messages` | Escucha y procesa mensajes entrantes del broker |
| `publicar` | Publica temperatura, humedad y parámetros cada `periodo` segundos |
| `destello` | Destella el LED integrado al recibir la orden |
| `control_rele` | Controla el relé cada 1 segundo según el modo activo |

---

## Publicación automática

**Tópico:** `e6614c311b912b31`

```json
{
  "temperatura": 26.2,
  "humedad": 44.5,
  "setpoint": 25.0,
  "periodo": 10,
  "modo": "AUTO"
}
```

---

## Mensajes que puede recibir desde el broker

Todos los mensajes se envían en formato `{"msg": valor}`.

| Tópico | Valor | Efecto |
|---|---|---|
| `e6614c311b912b31/setpoint` | `{"msg": 25.0}` | Actualiza la temperatura de corte |
| `e6614c311b912b31/periodo` | `{"msg": 10}` | Actualiza el intervalo de publicación en segundos (debe ser > 0) |
| `e6614c311b912b31/modo` | `{"msg": "AUTO"}` o `{"msg": "MANUAL"}` | Cambia el modo de operación del relé |
| `e6614c311b912b31/rele` | `{"msg": "True"}` o `{"msg": "False"}` | Activa/desactiva el relé (solo en modo MANUAL) |
| `e6614c311b912b31/destello` | `{"msg": "destello"}` | Destella el LED integrado por ~5 segundos |

---

## Lógica del relé (GP14, activo en LOW)

### Modo AUTO
- `temperatura > setpoint` → relé **activado**
- `temperatura <= setpoint` → relé **desactivado**

### Modo MANUAL
- `rele = True` → relé **activado**
- `rele = False` → relé **desactivado**

---

## Parámetros persistentes

Se guardan en `param_n_volat.json`.

| Parámetro | Tipo | Valor por defecto |
|---|---|---|
| `setpoint` | float | `25.0` |
| `periodo` | int | `10` |
| `modo` | string | `"MANUAL"` |
| `rele` | bool | `"False"` |
