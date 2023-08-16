import configparser
from lightcontroller import LightController
from shc_controller import SHCcontroller
from mqtt_lightcontroller import MQTTLightController
import asyncio

# Getting config
config = configparser.ConfigParser()
config.read('config.ini')

# EmonMQTT setup
username =      config['emonMQTT']['username']
password =      config['emonMQTT']['password']
emonhost =      config['emonMQTT']['host']
emonMQTTport =  int(config['emonMQTT']['port'])
MQTTprefix =   config['emonMQTT']['prefix']

# SHC setup
SHCusername =   config['SHC']['username']
SHCpassword =   config['SHC']['password']
SHChost =       config['SHC']['host']
SHCZone =       config['SHC']['zone']

# Making a request

async def main():
    shc = SHCcontroller(SHCusername, SHCpassword, SHChost, SHCZone)

    light_controller = LightController(shc, 1000)

    mqtt_controller = MQTTLightController(light_controller, emonhost, emonMQTTport, username, password, MQTTprefix)

    await mqtt_controller.run()

if __name__ == "__main__":
    asyncio.run(main())
