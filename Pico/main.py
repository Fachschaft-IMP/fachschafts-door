import sys
import time
import machine
import network
import urequests as requests

# Wi-Fi-Verbindung herstellen
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("Fachschaft IMP", "8clFBb:oR;Q/#scBBj")  # SSID und Passwort anpassen
while not wifi.isconnected():
    pass
print(f'local ip address: {wifi.ifconfig()[0]}')


WTD = machine.WDT() # Watchdog inizialisieren
BASE_URL = 'http://192.168.1.241:8000/?content='
SENSOR_PIN = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP) # Schalter an Pin GP14 konfigurieren
LED = machine.Pin("LED")

last_sensor_state = "doorOpen"

start_timer_request = time.time()
start_timer_reset = time.time()
request_duration = 60 * 60 # 60 minutes
reset_duration = 12 * 60 * 60 # 24 hours

print("starting while true")
while True:
    # Schalterzustand überprüfen
    sensor_state = "doorOpen" if SENSOR_PIN.value() else "doorClosed" 

    # Wenn sich der Schalterzustand ändert
    if sensor_state != last_sensor_state:
        last_sensor_state = sensor_state
        print(sensor_state)
        
        url = BASE_URL + sensor_state

        try:
            response = requests.get(url=url)
        except:
            pass


        LED.toggle()
        for i in range(5):
            WTD.feed()
            time.sleep(1.9)


    current_time = time.time()
    elapsed_time_request = current_time - start_timer_request
    elapsed_time_reset   = current_time - start_timer_reset

    # Jede 60 Minuten die Seite aufrufen, sodass sie nicht down geht
    if elapsed_time_request >= request_duration:
        url = BASE_URL + sensor_state
        try:
            response = requests.get(url=url)
        except:
            pass
        start_timer_request = current_time

    if elapsed_time_reset >= reset_duration:
        sys.exit()

    WTD.feed()
    
    time.sleep(1.9)