import asyncio
import websockets
import json
import django

django.setup()


def build_payload(guest_id, answer, game_id):
    return {"guest_id": guest_id, "answer": answer, "game_id": game_id}


class Websocket:
    def __init__(self):
        self.users = {}
        self.sockets = {}
        pass

    async def user_connect(self, websocket, user_data):
        guest_id = user_data["guestId"]
        self.users[guest_id] = user_data
        self.sockets[guest_id] = websocket

    async def get_gamestate(self, game_id, user_id):
        if len(self.users) > 0:
            user_copy = self.users.copy()
            test = False
            for i in filter(lambda elem: elem["gameId"] == game_id and elem["guestId"] != user_id
                    , user_copy.values()):
                test = i
            if test:
                return test

    async def get_user_data(self, websocket, guest_id):
        if len(self.users) > 0 and guest_id in self.users.keys():
            user_data = self.users[guest_id]
            game_state = await self.get_gamestate(user_data["gameId"], guest_id)
            if game_state is not None:
                message = build_payload(guest_id, game_state["answer"], user_data["gameId"])
                await websocket.send(json.dumps(message))

    async def player_2_connect(self, websocket, secondary_user_data):
        await self.user_connect(websocket, secondary_user_data)
        game_id = secondary_user_data["gameId"]
        user_id = secondary_user_data["guestId"]
        primary_user_data = await self.get_gamestate(game_id, user_id)
        primary_user_id = primary_user_data["guestId"]
        primary_answer = list(primary_user_data["answer"])
        secondary_user_id = secondary_user_data["guestId"]
        secondary_answer = list(secondary_user_data["answer"])

        primary_payload = build_payload(primary_user_id, secondary_answer, game_id)
        secondary_payload = build_payload(secondary_user_id, primary_answer, game_id)

        primary_socket = self.sockets[primary_user_data["guestId"]]
        await primary_socket.send(json.dumps(primary_payload))
        await websocket.send(json.dumps(secondary_payload))
        # del self.users[primary_user_id]
        # del self.users[secondary_user_id]
        # del self.sockets[primary_user_id]
        # del self.sockets[secondary_user_id]

    async def close_conns(self, websocket, decoded):
        gamestate = await self.get_gamestate(decoded["gameId"], decoded["guestId"])
        del self.users[decoded["guestId"]]
        del self.users[gamestate["guestId"]]
        await websocket.close()
        # await self.sockets[gamestate["guestId"]].close()
        # del self.sockets[gamestate["guestId"]]
        # del self.sockets[decoded["guestId"]]

    async def echo(self, websocket, path):
        async for message in websocket:
            decoded = json.loads(message)
            method = decoded["method"]
            if method == "player_1_connect":
                await self.user_connect(websocket, decoded)
            if method == "player_2_connect":
                await self.player_2_connect(websocket, decoded)
            if method == "kill":
                result = await self.close_conns(websocket, decoded)
            if method == "get_user_data":
                await self.get_user_data(websocket, decoded["guestId"])
            if method == "get_gamestate":
                gamestate = await self.get_user_data(websocket, decoded["guestId"])
                if gamestate is not None:
                    gamestate["guestId"] = decoded["guestId"]
                    await websocket.send(json.dumps(gamestate))

    async def main(self):
        uri = websockets.parse_uri(f"ws://0.0.0.0:8765/")
        # uri = websockets.parse_uri(f"ws://localhost:8765/")
        async with websockets.serve(ws_handler=self.echo, host=uri.host, port=uri.port):
            self.fut = asyncio.Future()
            await self.fut

    def run(self):
        asyncio.run(self.main())
