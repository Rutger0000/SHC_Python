import aiohttp

HEADERS = {
    'Accept': 'application/json'
}

class SHCcontroller:
    def __init__(self, username, password, address, zone):
        self.username = username
        self.password = password
        self.address = address
        self.zone = zone
        self.url = 'http://' + address + '/remote/json-rpc'

    async def fetch_data(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=data, headers=HEADERS, auth=aiohttp.BasicAuth(self.username, self.password)) as response:
                return await response.json()

    async def get_devices(self):
        data_get = {
            "jsonrpc": "2.0",
            "method": "StatusControlFunction/getDevices",
            "params": [self.zone, ""],
            "id": 1
        }
        result = await self.fetch_data(data_get)
        return result['result']

    async def set_dim(self, device_id, state):
        data_set = {
            "jsonrpc": "2.0",
            "method": "StatusControlFunction/controlDevice",
            "params": [self.zone, device_id, str(state)],
            "id": 1
        }
        return await self.fetch_data(data_set)

    async def set_power(self, device_id, state):
        data_set = {
            "jsonrpc": "2.0",
            "method": "StatusControlFunction/controlDevice",
            "params": [self.zone, device_id, 'on' if state else 'off'],
            "id": 1
        }
        return await self.fetch_data(data_set)

    async def set_light_dim_state(self, device_id, value):
        await self.send_light_state(device_id, value)



    


    
        
