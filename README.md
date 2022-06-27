# milasdk
Python SDK for Mila Air Purifiers.
The primary goal is to use this to power integrations for [Home Assistant](https://www.home-assistant.io/).

## Installation
```pip install milasdk```

## Usage
### Simple example

```
async def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)-8s %(message)s')

    #create the authenticated session
    async with DefaultAsyncSession(aiohttp.ClientSession(), USERNAME, PASSWORD) as session:
        api = MilaApi(session)

        while True:
            await update(api)
            await asyncio.sleep(60)
```

Please see `simple_example.py` for a full working example of usage of this library.

## Objects
### MilaAPI
The main client class that handles communications between the client and Mila service using GraphQL

## API Overview
The Mila GraphQL schema can be found in [mila_schema.gql](milasdk/gql/mila_schema.gql).

