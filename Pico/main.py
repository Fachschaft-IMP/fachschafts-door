import sys
import time
import machine
import urequests as requests
from Wifi import Wifi
import network

# wifi = Wifi("Fachschaft IMP", "8clFBb:oR;Q/#scBBj")
# wifi.wifiConnect()

led = machine.Pin("LED")


wifi = network.WLAN(network.STA_IF)
wifi.active(True)

def try_connect(max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        # WiFi-Schnittstelle aktivieren
        wifi.active(True)
        print('wifi-Verbindung herstellen:', "Fachschaft IMP")
        wifi.connect("Fachschaft IMP", "8clFBb:oR;Q/#scBBj")
        start_time = time.time()
        while not wifi.isconnected() and time.time() - start_time < 3:
            led.toggle()
            print('.', end='')
            time.sleep(.5)
        if wifi.isconnected():
            print("\nwifi-Verbindung hergestellt")
            print(f'local ip address: {wifi.ifconfig()[0]}')
            led.on()
            return True
        else:
            print("\nVerbindung fehlgeschlagen, versuche es erneut...")
            # WiFi-Schnittstelle deaktivieren, um sie zurückzusetzen
            wifi.active(False)
            time.sleep(1)  # Kurze Pause, um das Deaktivieren zu verarbeiten
            attempt += 1
    return False

try_connect()

# Watchdog inizialisieren
wtd = machine.WDT()

base_url = 'http://192.168.1.241:8000/?content='
# Schalter an Pin GP14 konfigurieren
sensor_pin = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

last_sensor_state = "doorOpen"

start_timer_request = time.time()
start_timer_reset = time.time()
request_duration = 60 * 60 # 60 minutes
reset_duration = 12 * 60 * 60 # 24 hours

while True:
    if not wifi.isconnected():
        print('wifi-Verbindung verloren, versuche neu zu verbinden')
        wifi.connect("Fachschaft IMP", "8clFBb:oR;Q/#scBBj")
        while not wifi.isconnected():
            led.toggle()
            print('.', end='')
            time.sleep(.5)
        print('wifi-Verbindung wiederhergestellt')
        print(f'local ip address: {wifi.ifconfig()[0]}')
        led.on()
    # Schalterzustand überprüfen
    sensor_state = "doorOpen" if sensor_pin.value() else "doorClosed" 

    # Wenn sich der Schalterzustand ändert
    if sensor_state != last_sensor_state:
        last_sensor_state = sensor_state
        # print(sensor_state)

        url = base_url + sensor_state

        try:
            response = requests.get(url=url)
        except:
            pass


        led.toggle()
        for i in range(5):
            wtd.feed()
            time.sleep(2)


    current_time = time.time()
    elapsed_time_request = current_time - start_timer_request
    elapsed_time_reset   = current_time - start_timer_reset

    # Jede 60 Minuten die Seite aufrufen, sodass sie nicht down geht
    if elapsed_time_request >= request_duration:
        url = base_url + sensor_state
        try:
            response = requests.get(url=url)
        except:
            pass
        start_timer_request = current_time

    if elapsed_time_reset >= reset_duration:
        sys.exit()

    wtd.feed()
    
    time.sleep(2)