import asyncio
import logging
import aiohttp

from credentials import USERNAME, PASSWORD
from milasdk import DefaultAsyncSession
from milasdk.api import MilaApi
from milasdk.gql import ApplianceSensorKind, SmartModeKind

from pprint import pprint as pp

_LOGGER = logging.getLogger(__name__)

async def introspection(api: MilaApi):
        r = await api.get_appliances()
        #r = await api.get_appliance("device here")
        #r = await api.get_appliance_sensor("device here", ApplianceSensorKind.Temperature)
        #r = await api.set_smart_mode("device here",SmartModeKind.ChildLock,True)
        # pp(r)
        print('Introspection Results')
        r = await api.introspection()
        pp(r)
        
        return r

async def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)-8s %(message)s')

    #create the authenticated session
    async with DefaultAsyncSession(aiohttp.ClientSession(), USERNAME, PASSWORD) as session:
        api = MilaApi(session)
        introspection_result = await introspection(api)
    
    schema_string = convert_introspection_to_sdl(introspection_result)
    
    with open('milasdk/gql/new_schema.gql', 'w') as fh:
        fh.write(schema_string)
        
def convert_introspection_to_sdl(introspection_result):
    # This function converts the introspection JSON result to SDL format
    # You need to implement this conversion based on your schema structure
    # Here is a simple placeholder example
    schema_sdl = ""
    for type_info in introspection_result['__schema']['types']:
        type_name = type_info['name']
        fields = type_info.get('fields', [])
        
        if fields is None:
            continue
        
        schema_sdl += f"type {type_name} {{\n"
        for field in fields:
            field_name = field['name']
            field_type = field['type']['name'] or field['type']['ofType']['name']
            schema_sdl += f"  {field_name}: {field_type}\n"
        schema_sdl += "}\n\n"
    return schema_sdl

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
