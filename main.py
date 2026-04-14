from mqtt_as import MQTTClient, config
import asyncio
from settings import SSID, password, BROKER, PORT
import dht, machine, json
from collections import OrderedDict
import guardar_param

d = dht.DHT22(machine.Pin(15))
rele = machine.Pin(14, machine.Pin.OUT)
rele.value(1)  # Inicia desactivado
led = machine.Pin("LED", machine.Pin.OUT)
destello_event = asyncio.Event()
# Local configuration
config['server'] = BROKER 
config['ssid'] = SSID
config['port'] = PORT
config['wifi_pw'] = password
config['ssl'] = True

async def destello():
    while True:
        await destello_event.wait()
        destello_event.clear()
        print("INICIANDO DESTELLO")
        for i in range(10):
            led.value(1)
            await asyncio.sleep_ms(250)
            led.value(0)
            await asyncio.sleep_ms(250)
        print("DESTELLO TERMINADO")
        
async def control_rele():
    while True:
        params = guardar_param.leer_params()
        temperatura_actual = d.temperature()
        
        if params["modo"] == "AUTO":
            if temperatura_actual > params["setpoint"]:
                rele.value(0)  # Activa el relé
            else:
                rele.value(1)  # Desactiva el relé
        elif params["modo"] == "MANUAL":
            rele.value(0) if params["rele"] else rele.value(1)
        
        await asyncio.sleep(1)

async def messages(client):
    async for topic, msg, retained in client.queue:
        t = topic.decode()
        m = msg.decode()
        print(f'Topic: "{t}" Message: "{m}" Retained: {retained}')
        
        if t == 'e6614c311b912b31/destello':
            destello_event.set()

        elif t == 'e6614c311b912b31/setpoint':
            try:
                dato = json.loads(m)           
                guardar_param.actualizar_parametro("setpoint", float(dato["msg"]))
                print(f"Setpoint actualizado: {m}")
            except ValueError:
                print(f"Setpoint inválido: {m}")
        
        elif t == 'e6614c311b912b31/modo':
            try:
                dato = json.loads(m)
                valor = dato["msg"]
                if valor in ("AUTO", "MANUAL"):
                    guardar_param.actualizar_parametro("modo", valor)
                    print(f"Modo actualizado: {valor}")
                else:
                    print(f"Modo inválido: {valor}")
            except (ValueError, KeyError):
                print(f"Modo inválido: {m}")
            
        elif t == 'e6614c311b912b31/rele':
            try:
                dato = json.loads(m)
                valor = str(dato["msg"])
                if valor in ("True", "False"):
                    guardar_param.actualizar_parametro("rele", valor == "True")
                    print(f"Relé actualizado: {valor}")
                else:
                    print(f"Relé inválido: {valor}")
            except (ValueError, KeyError):
                print(f"Relé inválido: {m}")

        elif t == 'e6614c311b912b31/periodo':
            try:
                dato = json.loads(m)
                valor = int(dato["msg"])
                if valor>=0:
                    guardar_param.actualizar_parametro("periodo", valor)
                    print(f"Periodo actualizado: {valor}")
                else:
                    print(f"Periodo inválido: {valor}")
            except (ValueError, KeyError):
                print(f"Periodo inválido: {m}")

async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe('e6614c311b912b31', 1)  # renew subscriptions
        await client.subscribe('e6614c311b912b31/setpoint', 1)  # renew subscriptions
        await client.subscribe('e6614c311b912b31/periodo', 1)  # renew subscriptions
        await client.subscribe('e6614c311b912b31/destello', 1)  # renew subscriptions
        await client.subscribe('e6614c311b912b31/modo', 1)  # renew subscriptions
        await client.subscribe('e6614c311b912b31/rele', 1)  # renew subscriptions

async def publicar(client):
    while True:
        try:
            params = guardar_param.leer_params()
            d.measure()
            try:
                temperatura = d.temperature()
            except OSError:
                print("sin sensor temperatura")
            try:
                humedad = d.humidity()
            except OSError:
                print("sin sensor humedad")

            datos = json.dumps(OrderedDict([
                ('temperatura', temperatura),
                ('humedad', humedad),
                ('setpoint', params["setpoint"]),
                ('periodo', params["periodo"]),
                ('modo', params["modo"])
            ]))
            await client.publish('e6614c311b912b31', datos, qos=1)
            await asyncio.sleep(params["periodo"])

        except OSError:
            print("sin sensor")
            await asyncio.sleep(10)

async def main(client):
    await client.connect()
    for coroutine in (up, messages, publicar):
        asyncio.create_task(coroutine(client))
    asyncio.create_task(destello())
    asyncio.create_task(control_rele())

    while True:
        await asyncio.sleep(60) 

config["queue_len"] = 1  # Use event interface with default queue size
MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors