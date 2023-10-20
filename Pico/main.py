import sys
import time
import ntptime
import machine
import network
import urequests as requests
from lib.umqtt.simple import MQTTClient

# CET Time in a tuble like time.gmtime()
def cettime():
    try:
        ntptime.settime()
    except:
        pass
    
    year = time.localtime()[0]       #get current year
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    if now < HHMarch :               # we are before last sunday of march
        cet=time.localtime(now+3600) # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet=time.localtime(now+7200) # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet=time.localtime(now+3600) # CET:  UTC+1H
    return(cet)

# Wi-Fi-Verbindung herstellen
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("Fachschaft IMP", "8clFBb:oR;Q/#scBBj")  # SSID und Passwort anpassen

while not wifi.isconnected():
    pass


# Watchdog inizialisieren
wtd = machine.WDT()

base_url = 'http://192.168.1.242:8000/?content='
# Schalter an Pin GP14 konfigurieren
sensor_pin = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin("LED")

last_sensor_state = "doorOpen"

start_timer_request = time.time()
start_timer_reset = time.time()
request_duration = 60 * 60 # 60 minutes
reset_duration = 12 * 60 * 60 # 24 hours



# MQTT-Konfiguration
mqttBroker = 'io.adafruit.com'
mqttClient = 'pico'
mqttUser = 'FachschaftIMP'
mqttPW = 'aio_SHsV37ObHftQVPWEnnGnUrSNtx2Z'
mqttTopic = "FachschaftIMP/feeds/fachschaft-offnungszeiten"

# Funktion: Verbindung zum MQTT-Server herstellen
def mqttConnect():
    if mqttUser != '' and mqttPW != '':
        print("MQTT-Verbindung herstellen: %s mit %s als %s" % (mqttClient, mqttBroker, mqttUser))
        client = MQTTClient(mqttClient, mqttBroker, user=mqttUser, password=mqttPW)
    else:
        print("MQTT-Verbindung herstellen: %s mit %s" % (mqttClient, mqttBroker))
        client = MQTTClient(mqttClient, mqttBroker)
    print("connecting to adafruit...")
    try:
        client.connect()
    except:
        with open('Output.txt', mode='a') as file:
            print('MQTT not able to connect %s' % cettime(), file=file)
        
    print()
    print('MQTT-Verbindung hergestellt')
    print()
    return client




while True:
    # Schalterzustand überprüfen
    sensor_state = "doorOpen" if sensor_pin.value() else "doorClosed"
    print(sensor_state) 

    # Wenn sich der Schalterzustand ändert
    if sensor_state != last_sensor_state:
        last_sensor_state = sensor_state
        
        url = base_url + sensor_state
        # print(url)
        try:
            response = requests.get(url=url)
        except:
            print("An exception occurred")
            with open("Output.txt", "a") as text_file:
                print("request failed %s" % cettime(), file=text_file)
        # response = requests.get(base_url + sensor_state)



        ###################################################################
        try:
            client = mqttConnect()
            if sensor_state == 'doorOpen':
                client.publish(mqttTopic, str(0))
                time.sleep(1)
                client.publish(mqttTopic, str(1))
            else:
                client.publish(mqttTopic, str(1))
                time.sleep(1)
                client.publish(mqttTopic, str(0))

            print("An Topic %s gesendet" %  mqttTopic)
            print()
            client.disconnect()
            print('MQTT-Verbindung beendet')
        except OSError:
            print()
            print('Fehler: Keine MQTT-Verbindung')
        ###############################################################


        led.toggle()
        # print("change")
        for i in range(5):
            wtd.feed()
            time.sleep(2)


    # Timer hochzählen lassen
    current_time = time.time()
    elapsed_time_request = current_time - start_timer_request
    elapsed_time_reset   = current_time - start_timer_reset

    # Jede 60 Minuten die Seite aufrufen, sodass sie nicht down geht
    if elapsed_time_request >= request_duration:
        url = base_url + sensor_state
        try:
            response = requests.get(url=url)
        except:
            with open("Output.txt", "w") as text_file:
                text_file.write("request failed in elapsed_time %s" % cettime())
        start_timer_request = current_time

    if elapsed_time_reset >= reset_duration:
        # machine.reset()
        sys.exit()
        start_timer_reset = current_time

    wtd.feed()
    
    time.sleep(2)