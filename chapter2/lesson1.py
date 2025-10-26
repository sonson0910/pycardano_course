from pycardano import BlockFrostChainContext, Network

BLOCKFROST_PROJECT_ID = "preprod0K9MnKqsU21MJvqu00V4Laf4pz7dALPK"

BASE_URL = "https://cardano-preprod.blockfrost.io/api"
context = BlockFrostChainContext(
    project_id=BLOCKFROST_PROJECT_ID,
    base_url=BASE_URL,
)

print(f'Connected to BlockFrost on {context.network} network.')


import asyncio
import websockets
import json


async def connect_to_websocket():
    host = "wss://ogmios144y67y8wjt9e6e5a4tn.cardano-preprod-v6.ogmios-m1.dmtr.host"

    async with websockets.connect(host) as websocket:
        print(f"Connected to {host}")

        event = {
            "jsonrpc": "2.0",
            "method": "queryLedgerState/utxo",
            "params": {
                "addresses": [
                    "addr_test1wraqlpezmu3h9n9mxey6y03u2sdd0e8cyx9n2qxscz6staczrlnuj"
                ]
            },
        }

        await websocket.send(json.dumps(event))
        response = await websocket.recv()
        print(f"Received from server: {response}")

    print("WebSocket connection closed.")


asyncio.get_event_loop().run_until_complete(connect_to_websocket())
