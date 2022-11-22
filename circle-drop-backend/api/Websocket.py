import asyncio
import websockets
import json
import django
from random import randrange
from datetime import datetime
import math

django.setup()

class Websocket:
    def __init__(self):
        self.games = {}
        self.sockets = {}
        self.times = {}
        self.loss_time = 40
        self.loss_percent = .1
        self.original_shape_size = 10000
        self.round_place = {}
        self.scoring = {0: 5, 1: 3, 2: 1}
        pass

    async def send_all_players(self, game_id, payload=None):
        if payload is None:
            payload = {}
        if payload == {}:
            payload = {"method": "gamestate", "gameId": game_id, "data": self.games[game_id]}
        keys = self.games[game_id].keys()
        for key in keys:
            await self.sockets[key].send(json.dumps(payload))

    async def update_gamestate(self, decoded):
        game_id = decoded["gameId"]
        guest_id = decoded["guestId"]
        guest = self.games[game_id][guest_id]
        guest["waiting"] = True
        guest["size"] = decoded["data"]["size"]
        guest["hasLost"] = (sum(guest["times"]) > 40) or ((guest["size"][0] * guest["size"][1] / self.original_shape_size) < self.loss_percent)
        if not guest["hasLost"]:
            guest["times"].append(round(datetime.now().timestamp() - self.times[game_id], 4))
            self.round_place[game_id].append(guest_id)
        # calculate place
        for i, guestId in enumerate(self.round_place[game_id]):
            if guest_id == guestId:
                self.games[game_id][guestId]["score"] += self.scoring.get(i, 0)
        await self.send_all_players(game_id)

    async def reset_waiting(self, decoded):
        game_id = decoded["gameId"]
        game = self.games[game_id]
        not_lost = []
        for guestId in game.keys():
            if not game[guestId]["hasLost"]:
                not_lost.append(guestId)
                game[guestId]["waiting"] = False
        if len(not_lost) == 0 and game_id in self.times.keys():
            top_score = max([game[guestId]["score"] for guestId in game])
            winner = [key for key, value in game.items() if value["score"] == top_score]
            await self.send_all_players(game_id, payload={"method": "winner", "data": winner[0]})
        else:
            self.times[game_id] = datetime.now().timestamp()
            self.round_place[game_id] = []
            await self.send_all_players(game_id)

    async def user_connect(self, websocket, decoded):
        game_id = decoded["gameId"]
        guest_id = decoded["guestId"]
        self.sockets.update({guest_id: websocket})
        self.games[game_id][guest_id] = decoded["data"]
        self.games[game_id][guest_id]["size"] = [math.sqrt(self.original_shape_size), math.sqrt(self.original_shape_size)]
        self.games[game_id][guest_id]["score"] = 0
        await self.send_all_players(game_id)

    async def create_game(self, websocket, decoded):
        game_id = decoded["gameId"]
        guest_id = decoded["guestId"]
        self.games[game_id] = {}
        self.games[game_id][guest_id] = decoded["data"]
        self.games[game_id][guest_id]["hasLost"] = False
        self.games[game_id][guest_id]["size"] = [math.sqrt(self.original_shape_size), math.sqrt(self.original_shape_size)]
        self.games[game_id][guest_id]["score"] = 0
        self.sockets[guest_id] = websocket
        self.times[game_id] = 0
        self.round_place[game_id] = []
        await websocket.send(json.dumps({"method": "gamestate", "gameId": game_id, "data": self.games[game_id]}))

    async def get_gamestate(self, websocket, game_id):
        websocket.send(json.dumps({"method": "gamestate", "data": self.games[game_id]}))

    async def send_player_info(self, game_id):
        await self.send_all_players(game_id)

    async def close_conns(self, websocket, decoded):
        del self.games[decoded["gameId"]]

    def get_new_pos(self):
        return [randrange(1000), randrange(1000), randrange(1000), randrange(1000)]

    async def echo(self, websocket, path):
        async for message in websocket:
            decoded = json.loads(message)
            method = decoded["method"]
            if method == "player_connect":
                await self.user_connect(websocket, decoded)
            if method == "create_game":
                await self.create_game(websocket, decoded)
            if method == "start":
                self.times[decoded["gameId"]] = datetime.now().timestamp()
                payload = {"method": "start", "gameId": decoded["gameId"], "data": self.get_new_pos()}
                await self.send_all_players(decoded["gameId"], payload)
            if method == "kill":
                await self.close_conns(websocket, decoded)
                await websocket.send(json.dumps({"method": "allGames", "allGames": True, "data": self.games}))
            if method == "get_gamestate":
                await self.get_gamestate(websocket, decoded["gameId"])
            if method == "get_all_games":
                await websocket.send(json.dumps({"method": "allGames", "allGames": True, "data": self.games}))
            if method == "update_gamestate":
                await self.update_gamestate(decoded)
            if method == "reset_waiting":
                payload = {"method": "start", "gameId": decoded["gameId"], "data": self.get_new_pos()}
                await self.send_all_players(decoded["gameId"], payload)
                await self.reset_waiting(decoded)

    async def main(self):
        uri = websockets.parse_uri(f"ws://0.0.0.0:8765/")
        # uri = websockets.parse_uri(f"ws://localhost:8765/")
        async with websockets.serve(ws_handler=self.echo, host=uri.host, port=uri.port):
            self.fut = asyncio.Future()
            await self.fut

    def run(self):
        asyncio.run(self.main())
