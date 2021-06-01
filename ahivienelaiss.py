# ahivienelaiss
# un señalizador visual que indica cuanto tiempo falta para que pase la ISS por una ubicacion geografica determinada
# utilizando los datos que ofrece http://open-notify.org/ y la libreria neopixel con una tira de 60 LEDs
# donde en la mayoria de los casos cada LED representa un minuto, pero tambien se representan dias y horas.
# la primera version de este proyecto se ha ejecutado en un Raspberry Pi Zero W y requiere de conectividad WiFi
# para poder llamar al API que contiene la informacion sobre la ISS y tener la fecha/hora del sistema actualizada
# https://open-notify-api.readthedocs.io/en/latest/iss_pass.html

import urllib.request # para llamar al URL del API de la ISS
import json # para procesar la respuesta JSON del API de la ISS
import time # para tener acceso a la hora
from math import floor # libreria para contar con funciones matematicas y poder redondear numeros reales
import board # la  libreria de CircuitPython para controlar los LEDS
import neopixel # para poder encender y apagar los LEDS

def leds_24horas(segundos, color):
        # representar las 24 horas en 60 leds. Cada LED representa 2,5 horas
        segundos_led = segundos_dia / cuantos_led
        arreglo_leds = []
        leds2light = floor(segundos / segundos_led)
        for i in range(0,cuantos_led):
                if  i < leds2light:
                        arreglo_leds.append(color)
                else:
                        arreglo_leds.append((0,0,0))
        return arreglo_leds

def leds_1hora(segundos, color):
        # cada LED representa 1 minuto
        segundos_led = segundos_hora / cuantos_led
        arreglo_leds = []
        leds2light = floor(segundos / segundos_led)
        for i in range(0,cuantos_led):
                if  i < leds2light:
                        arreglo_leds.append(color)
                else:
                        arreglo_leds.append((0,0,0))
        return arreglo_leds

# La ubicacion geografica/altitud donde nos encontramos
latitud=40.477048
longitud=-3.697266
altura=100

cuantos_led = 60 # cuantos LEDs tiene nuestra tira
segundos_dia = 86400 # segundos del dia
segundos_hora = 3600 # segundos por hora

idle_time = 1 # tiempo muerto definido a 1 segundo inicialmente

# R,G,B
leds_off = (0,0,0) # led apagado
soft_blue = (0,0,10) # azul tenue para cuando la ISS se aleja
color_dias = (50,0,0) # rojo
color_horas = (255,80,0) # naranja
color_10minutos = (100,100,0) #  amarillo verdoso
color_minutos = (0,100,0) # verde manzana si faltan menos de 60 minutos para que la ISS este visible / pasando
color_pasando = (0,200,0) # verde manzana intenso si la ISS es visible / pasando

# mostramos todos los codigos de colores al inicio del programa
pixels = neopixel.NeoPixel(board.D18, cuantos_led, auto_write=False) # inicializamos y definimos el pin 18 del Raspberry Pi para controlar la tira de LEDS
pixels.fill(soft_blue)
pixels.show()
time.sleep(idle_time)
pixels.fill(color_dias)
pixels.show()
time.sleep(idle_time)
pixels.fill(color_horas)
pixels.show()
time.sleep(idle_time)
pixels.fill(color_10minutos)
pixels.show()
time.sleep(idle_time)
pixels.fill(color_minutos)
pixels.show()
time.sleep(idle_time)
pixels.fill(color_pasando)
pixels.show()
time.sleep(idle_time)

ISS_API = "http://api.open-notify.org/iss-pass.json?lat=" + str(latitud) + "&lon=" + str(longitud) + "&alt=" + str(altura)

while True:
        time.sleep(idle_time)
        pixels.fill(leds_off)
        pixels.show()
        # llamamos al API
        with urllib.request.urlopen(ISS_API) as url:
                data = json.loads(url.read().decode())
                print(data)
                proximo_paso = data['response'][0]['risetime']
                segundos_para_proximo_paso = data['response'][0]['risetime'] - time.time()
                print('Risetime: ', data['response'][0]['risetime'])
                print('Time: ', time.time())
                print('Segundos: ', segundos_para_proximo_paso)
                # dependiendo del tiempo faltante se muestra un codigo de colores diferente
                if segundos_para_proximo_paso > segundos_dia:
                        print('Falta(n) Dia(s)')
                        arreglo_leds = [color_dias] * cuantos_led
                        idle_time = 600
                elif segundos_para_proximo_paso > segundos_hora:
                        minutes2go = segundos_para_proximo_paso / 60
                        hours2go = minutes2go / 60
                        print('Falta(n)', hours2go, 'Hora(s)')
                        arreglo_leds = leds_24horas(segundos_para_proximo_paso, color_horas)
                        idle_time = 60
                elif segundos_para_proximo_paso > 600:
                        print('Faltan', (segundos_para_proximo_paso/60),  'Minutos')
                        arreglo_leds = leds_1hora(segundos_para_proximo_paso, color_10minutos)
                        idle_time = 10
                elif segundos_para_proximo_paso > 60:
                        print('Faltan', (segundos_para_proximo_paso/60),  'Minutos')
                        arreglo_leds = leds_1hora(segundos_para_proximo_paso, color_minutos)
                        idle_time = 2
                elif segundos_para_proximo_paso < -600:
                        arreglo_leds = [soft_blue] * cuantos_led
                        idle_time = 60
                else:
                        print('La ISS está pasando')
                        arreglo_leds = [color_pasando] * cuantos_led
                        idle_time = 10

        print(arreglo_leds) # mostrar la configuracion de cada led en la consola
        for i in range(0,cuantos_led):
                pixels[i] = arreglo_leds[i] # asignar al controlador de la tira de leds el valor de cada led
        pixels.show() # mostrar en la tira de leds los valores previamente asignados
