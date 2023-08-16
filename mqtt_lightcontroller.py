import paho.mqtt as mqtt
import asyncio_mqtt as aiomqtt
import json

class MQTTLightController:
    def __init__(self, light_controller, mqtt_broker, mqtt_port, mqtt_user, mqtt_password, mqtt_prefix):
        self.light_controller = light_controller
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.sub_client = aiomqtt.Client(self.mqtt_broker, self.mqtt_port, username=self.mqtt_user, password=self.mqtt_password)
        self.pub_client = aiomqtt.Client(self.mqtt_broker, self.mqtt_port, username=self.mqtt_user, password=self.mqtt_password)
        self.mqtt_prefix = mqtt_prefix
        self.light_controller.set_publisher(self)

    async def run(self):
        async with self.sub_client as client:
            async with client.messages() as messages:
                await self.refresh()
                
                await client.subscribe(f"{self.mqtt_prefix}/ctrl/#")
                await client.subscribe(f"{self.mqtt_prefix}/ctrl/#")

                async for message in messages:
                    if message.topic.matches(f"{self.mqtt_prefix}/ctrl/+/DIM"):
                        light_id = str(message.topic).split("/")[2]
                        await self.light_controller.set_dim(light_id, int(message.payload))
                        print("Setting dim of light", light_id, "to", message.payload)
                    elif message.topic.matches(f"{self.mqtt_prefix}/ctrl/+/POWER"):
                        light_id = str(message.topic).split("/")[2]
                        await self.light_controller.set_power(light_id, message.payload == b"true")
                        print("Setting power of light", light_id, "to", message.payload)
                    elif message.topic.matches(f"{self.mqtt_prefix}/ctrl/REFRESH"):
                        print("Refreshing all lights")
                        await self.refresh()
                        
    async def refresh(self):
        await self.refreshing(True)
        await self.light_controller.get_all_lights()
        await self.refreshing(False)

    async def refreshing(self, state):
        async with self.pub_client as client:
            await client.publish(f"{self.mqtt_prefix}/state/REFRESHING", state, retain=True)

                    
    async def publish(self, lights):
        async with self.pub_client as client:
            for light_id, light in lights.items():
                await client.publish(f"{self.mqtt_prefix}/state/{light_id}/STATE", json.dumps(light), retain=True)
    
    async def publish_single(self, light_id, light):
        async with self.pub_client as client:
            await client.publish(f"{self.mqtt_prefix}/state/{light_id}/STATE", json.dumps(light), retain=True)