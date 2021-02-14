import json
import asyncio


status = {}
sn = {}
clients = {}
snType = {}

async def addClient(token, name, client):
    global clients
    if token not in clients:
        clients[token] = {}
    clients[token][name] = client


async def deleteClient(token, name, client):
    global clients
    del clients[token][name]


async def addStatus(data, token, name):
    global sn, status
    if data['sn'] == sn[token][name]:
        if token not in status:
            status[token] = {}
        status[token][name] = {
            'status': 'online',
            'version': data['version'],
            'onlinePlayer': data['onlinePlayer']
        }


async def addSnType(token, sn, sntype):
    global snType
    sn = str(sn)
    if token not in snType:
        snType[token] = {}
    snType[token][sn] = sntype


async def getSnType(token, sn):
    global snType
    sn = str(sn)
    if token not in snType:
        return 'run'
    elif sn not in snType[token]:
        return 'run'
    else:
        return snType[token][sn]


async def getAllStatus(token):
    global sn, status, clients
    if token not in clients:
        return None
    if token not in status:
        status[token] = {}
    status[token] = {}
    if token not in sn:
        sn[token] = {}
    for client in clients[token]:
        if client not in sn[token]:
            sn[token][client] = 0
        sn[token][client] += 1
        data = {
            'type': 'status',
            'name': '__ALL__',
            'sn': sn[token][client]
        }
        try:
            await clients[token][client].send_str(json.dumps(data))
        except Exception:
            status[token][client] = {'status': 'offline'}
    await asyncio.sleep(0.5)
    return status[token]


async def checkServer(token, server):
    global sn, status, clients
    if token not in clients:
        return False
    if server not in clients[token]:
        return False
    if token not in status:
        status[token] = {}
    status[token][server] = {}
    if token not in sn:
        sn[token] = {}
    if server not in sn[token]:
        sn[token][server] = 0
    sn[token][server] += 1
    data = {
        'type': 'status',
        'name': str(server),
        'sn': sn[token][server]
    }
    try:
        await clients[token][server].send_str(json.dumps(data))
    except Exception:
        return False
    await asyncio.sleep(0.2)
    if 'status' not in status[token][server]:
        return False
    if status[token][server]['status'] == 'online':
        return True
    return False


async def runCommand(token, server, command):
    global sn, status, clients
    serverStatus = await checkServer(token, server)
    if not serverStatus:
        return 'offline'
    else:
        sn[token][server] += 1
        data = {
            'type': 'command',
            'name': str(server),
            'sn': sn[token][server],
            'command': command
        }
        try:
            await clients[token][server].send_str(json.dumps(data))
            return sn[token][server]
        except Exception:
            return 'failure'
