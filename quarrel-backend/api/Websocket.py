import asyncio
import websockets
import json
import django

django.setup()


def build_payload(guest_id, answer):
    return {"guest_id": guest_id, "answer": answer}


class Websocket:
    def __init__(self):
        self.games = {}
        pass

    async def player_1_connect(self, primary_user_data):
        game_id = primary_user_data["gameId"]
        self.games[game_id] = primary_user_data
        print(self.games)

    async def player_2_connect(self, websocket, secondary_user_data):
        game_id = secondary_user_data["gameId"]
        primary_user_data = self.games[game_id]
        primary_user_id = primary_user_data["guestId"]
        primary_answer = list(primary_user_data["answer"])
        secondary_user_id = secondary_user_data["guestId"]
        secondary_answer = list(secondary_user_data["answer"])

        primary_payload = build_payload(primary_user_id, secondary_answer)
        secondary_payload = build_payload(secondary_user_id, primary_answer)
        await websocket.send(json.dumps(primary_payload))
        await websocket.send(json.dumps(secondary_payload))
        del self.games[game_id]

    async def close_conns(self, websocket):
        await websocket.close()

    async def echo(self, websocket, path):
        async for message in websocket:
            decoded = json.loads(message)
            method = decoded["method"]
            if method == "player_1_connect":
                await self.player_1_connect(decoded)
            if method == "player_2_connect":
                await self.player_2_connect(websocket, decoded)
            if method == "kill":
                result = await self.close_conns(websocket)

    async def main(self):
        uri = websockets.parse_uri(f"ws://localhost:8765/")
        async with websockets.serve(ws_handler=self.echo, host=uri.host, port=uri.port):
            self.fut = asyncio.Future()
            await self.fut

    def run(self):
        asyncio.run(self.main())
