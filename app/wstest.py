import asyncio
import websockets

async def test_ws():
    #uri = "ws://localhost:8000/seedor/1.0/ws/user123"
    uri = "wss://apiuat.seedors.com/seedor/1.0/ws/user123"
    async with websockets.connect(uri) as websocket:
        print("Connected")
        await websocket.send("Hello from Python")
        await asyncio.sleep(10)

asyncio.run(test_ws())
