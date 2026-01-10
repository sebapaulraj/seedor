import asyncio
import websockets

async def test_ws():
    uri = "ws://localhost:8000/seedor/1.0/ws/muthukumar"
    # uri = "wss://apiuat.seedors.com/seedor/1.0/ws/user123"

    async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as websocket:
        print("Connected")

        await websocket.send("Hello from Python")

        # Keep alive for 10 minutes (600 seconds)
        await asyncio.sleep(6000)

        print("Closing connection")

asyncio.run(test_ws())
