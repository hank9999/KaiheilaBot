import json
from aiohttp import web
import aiohttp
import datetime
import asyncio
from config import getServerConfig, getWsConfig, getChannel, getFunctionSwitch
from khlBot import bot
from cardMessage import actionMessage
from serverUtils import addStatus, addClient, deleteClient


async def websocket_handler(request):
    global clients
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    query = dict(request.query)
    if 'token' not in query:
        await ws.close(code=1000, message=b'No Token')
        print(f'[{datetime.datetime.now().strftime("%m-%d %H:%M:%S")}] {request.remote} No token')
        return ws
    serverConfig = getServerConfig(query['token'])
    if serverConfig is None:
        await ws.close(code=1000, message=b'Wrong Token')
        print(f'[{datetime.datetime.now().strftime("%m-%d %H:%M:%S")}] {request.remote} {query["token"]} Wrong Token')
        return ws
    if 'name' not in query:
        await ws.close(code=1000, message=b'No Name')
        print(f'[{datetime.datetime.now().strftime("%m-%d %H:%M:%S")}] {request.remote} {query["token"]} No Name')
        return ws
    if len(query['name']) == 0:
        await ws.close(code=1000, message=b'Empty Name')
        print(f'[{datetime.datetime.now().strftime("%m-%d %H:%M:%S")}] {request.remote} {query["token"]} Empty Name')
        return ws
    await addClient(query['token'], query['name'], ws)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            print(f'[{datetime.datetime.now().strftime("%m-%d %H:%M:%S")}] {request.remote} {query["token"]} {query["name"]} {msg.data}')
            await dataProcess(msg.data, query['token'], query['name'])
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f'[{datetime.datetime.now().strftime("%m-%d %H:%M:%S")}] {request.remote} {query["token"]} {query["name"]} ws connection closed with exception {ws.exception()}')
    print(f'[{datetime.datetime.now().strftime("%m-%d %H:%M:%S")}] {request.remote} {query["token"]} {query["name"]} websocket connection closed')

    return ws


async def dataProcess(data, token, name):
    data = json.loads(data)
    if data['type'] == 'Login':
        if getFunctionSwitch(token, 'Login'):
            channel_id = getChannel(token, 'Login')
            message = actionMessage('登入', data['username'], name)
            await bot.send(str(channel_id), type=10, content=message)
    elif data['type'] == 'Logout':
        if getFunctionSwitch(token, 'Logout'):
            channel_id = getChannel(token, 'Logout')
            message = actionMessage('登出', data['username'], name)
            await bot.send(str(channel_id), type=10, content=message)
    elif data['type'] == 'Chat':
        if getFunctionSwitch(token, 'Chat'):
            channel_id = getChannel(token, 'Chat')
            await bot.send(str(channel_id), type=1, content=f'{datetime.datetime.now().strftime("%m-%d %H:%M:%S")} {data["username"]}: {data["text"]}')
    elif data['type'] == 'log':
        if getFunctionSwitch(token, 'log'):
            channel_id = getChannel(token, 'log')
            await bot.send(str(channel_id), type=1, content=str(data['log']))
    elif data['type'] == 'PlayerCommand':
        if getFunctionSwitch(token, 'PlayerCommand'):
            channel_id = getChannel(token, 'PlayerCommand')
            message = actionMessage('玩家执行指令', data['username'], name, data['command'])
            await bot.send(str(channel_id), type=10, content=message)
    elif data['type'] == 'RconCommand':
        if getFunctionSwitch(token, 'RconCommand'):
            channel_id = getChannel(token, 'RconCommand')
            message = actionMessage('Rcon执行指令', 'Rcon', name, data['command'])
            await bot.send(str(channel_id), type=10, content=message)
    elif data['type'] == 'status':
        await addStatus(data, token, name)
    elif data['type'] == 'command':
        if getFunctionSwitch(token, 'commandReturn'):
            channel_id = getChannel(token, 'command')
            await bot.send(str(channel_id), type=1, content=f'sn: {data["sn"]}\n{data["return"]}')
    else:
        pass


def serverWsRun():
    loop = asyncio.get_event_loop()
    wsConfig = getWsConfig()
    app = web.Application()
    app.add_routes([web.get(wsConfig['path'], websocket_handler)])
    runner = aiohttp.web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = aiohttp.web.TCPSite(runner, host=wsConfig['host'], port=wsConfig['port'])
    loop.run_until_complete(site.start())
