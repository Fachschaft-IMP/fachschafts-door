import network
import machine
import time

class Wifi:
    def __init__(self, ssid:str, password:str, led=machine.Pin('LED')):
        self.ssid = ssid
        self.password = password
        self.led = led

    def wifiConnect(self) -> None:
        """
        establish a wifi connection, while the LED is blinking
        """
        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)

        if not wifi.isconnected():
            print('wifi-Verbindung herstellen:', self.ssid)
            wifi.connect(self.ssid, self.password)
            while not wifi.isconnected():
                self.led.toggle()
                print('.', end='')
                time.sleep(1)
        print("")
        print('wifi-Verbindung hergestellt')
        print(f'local ip address: {wifi.ifconfig()[0]}')
        self.led.on()