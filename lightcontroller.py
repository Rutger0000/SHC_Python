import time

class LightController:
    def __init__(self, controller_delegate, refresh_interval):
        self.lights = {}
        self.delegate = controller_delegate
        self.last_refresh = 0
        self.refresh_interval = refresh_interval

    def set_publisher(self, publisher):
        self.publisher = publisher

    async def refresh(self):
        print("Refreshing lights...")
        devices = await self.delegate.get_devices()
        await self.update_state(devices)
        self.last_refresh = time.time()

    async def notify_publisher(self):
        if self.publisher:
            await self.publisher.publish(self.lights)

    async def notify_publisher_single(self, light_id):
        if self.publisher:
            await self.publisher.publish_single(light_id, self.lights[light_id])

    async def update_state(self, data):
        for item in data:
            if item['type'] != 'DimActuator':
                continue
            
            light_id = item['id']
            if light_id not in self.lights:
                self.lights[light_id] = {
                    'name': item['name'],
                    'type': item['type'],
                    'value': int(item['value']),
                    'on': True if item['value'] != '0' else False,
                }
            else:
                self.lights[light_id]['value'] = int(item['value']) if item['value'] != '0' else self.lights[light_id]['value']
                self.lights[light_id]['on'] = True if item['value'] != '0' else False

        print("Updated lights. Currently {} lights.".format(len(self.lights)))
        await self.notify_publisher()
    
    async def get_light_state(self, light_id):
        await self.check_refresh()
        if light_id in self.lights:
            return self.lights[light_id]['on']
        else:
            return None
        
    async def get_light_dim_state(self, light_id):
        await self.check_refresh()
        if light_id in self.lights:
            return self.lights[light_id]['value']
        else:
            return None

    async def get_all_lights(self):
        await self.refresh()
        return self.lights
    
    async def set_power(self, light_id, state):
        if light_id in self.lights:
            # setting power state
            await self.delegate.set_power(light_id, state)

            # updating state
            self.lights[light_id]['on'] = state
            await self.notify_publisher_single(light_id)

    async def set_dim(self, light_id, state):
        if light_id in self.lights:
            # setting dim state
            await self.delegate.set_dim(light_id, state)

            # updating state
            self.lights[light_id]['value'] = state
            if self.lights[light_id]['on'] == False:
                self.lights[light_id]['on'] = True
            await self.notify_publisher_single(light_id)

    async def check_refresh(self):
        if self.last_refresh + self.refresh_interval < time.time():
            await self.refresh()

