import json
import os
import sys


def getBotConfig():
    try:
        with open('botConfig.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
            if len(config['client_id']) == 0:
                raise Exception('Empty botConfig Client ID')
            if len(config['client_secret']) == 0:
                raise Exception('Empty botConfig Client Secret')
            if len(config['token']) == 0:
                raise Exception('Empty botConfig Token')
            if config['type'] == 'webhook' and len(config['verify_token']) == 0:
                raise Exception('Empty botConfig Verify Token')
            return config
    except Exception as e:
        print(e)
        sys.exit(1)


def getWsConfig():
    try:
        with open('wsConfig.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
            if len(config['host']) == 0:
                raise Exception('Empty wsConfig host')
            if not isinstance(config['port'], int):
                raise Exception('Wrong type wsConfig port')
            if len(config['path']) == 0:
                raise Exception('Empty wsConfig path')
            return config
    except Exception as e:
        print(e)
        sys.exit(1)


def createMapping():
    try:
        mappingTable = {}
        for root, dirs, files in os.walk('serverConfig/'):
            for f in files:
                file_address = os.path.join(root, f)
                with open(file_address, 'r', encoding='utf-8') as f1:
                    config = json.loads(f1.read())
                    if config['guild_id'] != 0:
                        mappingTable[config['guild_id']] = str(f).replace('.json', '')

        with open('mappingTable.json', 'w', encoding='utf-8') as f2:
            f2.write(json.dumps(mappingTable))
    except Exception as e:
        print(e)
        sys.exit(1)


def getToken(guild_id):
    with open('mappingTable.json', 'r', encoding='utf-8') as f:
        mappingTable = json.loads(f.read())
    if str(guild_id) in mappingTable:
        return mappingTable[str(guild_id)]
    else:
        return None


def getServerConfig(token):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
                return config
        else:
            return None
    except Exception as e:
        print(e)
        return None


def setToken(token, guild_id):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
            if config['guild_id'] != 0:
                return '该token已被绑定, 如有疑问请联系管理'
            config['guild_id'] = int(guild_id)
            with open(configDir, 'w', encoding='utf-8') as f:
                f.write(json.dumps(config))
            createMapping()
            return '设置成功, 随后请记得设置频道'
        else:
            return '未知的token'
    except Exception as e:
        print(e)
        return '设置失败'


def unsetToken(token, guild_id):
    try:
        with open('mappingTable.json', 'r', encoding='utf-8') as f:
            mappingTable = json.loads(f.read())
        if str(guild_id) in mappingTable:
            configDir = f'serverConfig/{token}.json'
            if os.path.exists(configDir):
                with open(configDir, 'r', encoding='utf-8') as f:
                    config = json.loads(f.read())
                config['guild_id'] = 0
                config['channel_id'] = 0
                for function in config['function']['receive']:
                    config['function']['receive'][function]['channel_id'] = -1
                    config['function']['receive'][function]['enable'] = False
                for function in config['function']['send']:
                    config['function']['send'][function]['enable'] = False
                for pm in config['permission']:
                    config['permission'][pm] = []
                with open(configDir, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(config))
                createMapping()
                return '已解绑token'
            else:
                return '未配置token'
        else:
            return '未配置token'
    except Exception as e:
        print(e)
        return '设置失败'


def setChannel(token, channel_id, function):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
            if function == 'default':
                config['channel_id'] = int(channel_id)
            elif function == 'reset':
                for function in config['function']['receive']:
                    config['function']['receive'][function]['channel_id'] = -1
            else:
                if function in config['function']['receive']:
                    config['function']['receive'][function]['channel_id'] = int(channel_id)
                elif function in config['function']['send']:
                    return '该功能无需设置频道'
                else:
                    return '未知的功能名称'
            with open(configDir, 'w', encoding='utf-8') as f:
                f.write(json.dumps(config))
            return '设置成功'
        else:
            return '已获取token但未获取到配置文件, 请重试.\n若多次出现请联系管理'
    except Exception as e:
        print(e)
        return '设置失败'


def setFunctionSwitch(token, function, boolean):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            return '已获取token但未获取到配置文件, 请重试.\n若多次出现请联系管理'
        if function in config['function']['receive']:
            if boolean == 'true':
                config['function']['receive'][function]['enable'] = True
            elif boolean == 'false':
                config['function']['receive'][function]['enable'] = False
            else:
                return '无效的布尔值 启用(true)还是关闭(false)呢?'
        elif function in config['function']['send']:
            if boolean == 'true':
                config['function']['send'][function]['enable'] = True
            elif boolean == 'false':
                config['function']['send'][function]['enable'] = False
            else:
                return '无效的布尔值 启用(true)还是关闭(false)呢?'
        else:
            return '未知的功能名称'

        with open(configDir, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config))
        return '设置成功'

    except Exception as e:
        print(e)
        return '设置失败'


def getFunctionSwitch(token, function):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            return None
        if function in config['function']['receive']:
            return config['function']['receive'][function]['enable']
        elif function in config['function']['send']:
            return config['function']['send'][function]['enable']
        else:
            return None

    except Exception as e:
        print(e)
        return None


def getChannel(token, function):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            return None

        if function in config['function']['receive']:
            if config['function']['receive'][function]['channel_id'] == -1:
                return config['channel_id']
            else:
                return config['function']['receive'][function]['channel_id']
        elif function in config['function']['send']:
            return config['channel_id']
        else:
            return None
    except Exception as e:
        print(e)
        return None


def checkAdmin(token, userId):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
            if userId in config['admin']:
                return True
            else:
                return False
        else:
            return None
    except Exception as e:
        print(e)
        return None


def checkPermission(token, function, roleIds):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
            if function not in config['permission']:
                return False
            else:
                hasPermission = False
                if 0 in config['permission'][function]:
                    return True
                for roleId in roleIds:
                    if roleId in config['permission'][function]:
                        hasPermission = True
                return hasPermission
        else:
            return None
    except Exception as e:
        print(e)
        return None


def operationPermission(token, operationType, function, roleId):
    if not roleId.isdigit():
        return '含有非数字字符'
    else:
        roleId = int(roleId)
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            return None
        if operationType == 'add':
            if function in config['permission']:
                if roleId in config['permission'][function]:
                    return '该角色已在该功能权限列表中'
                else:
                    config['permission'][function].append(roleId)
            else:
                return '该功能无需权限设置'
        elif operationType == 'del':
            if function in config['permission']:
                if roleId in config['permission'][function]:
                    config['permission'][function].remove(roleId)
                else:
                    return '该角色不在该功能权限列表中'
            else:
                return '该功能无需权限设置'
        else:
            return '没有这个操作类型'
        with open(configDir, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config))
        return '设置成功'
    except Exception as e:
        print(e)
        return None


def checkFilter(token, function, data):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
            if function in config['function']['receive']:
                for filter in config['function']['receive'][function]['filter']:
                    if str(data).find(str(filter)) >= 0:
                        return True
                return False
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False

def operationFilter(token, operationType, function, keyword):
    keyword = str(keyword)
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            return None
        if operationType == 'add':
            if function in config['function']['receive']:
                if keyword in config['function']['receive'][function]['filter']:
                    return '该关键词已在该功能过滤关键词中'
                else:
                    config['function']['receive'][function]['filter'].append(keyword)
            else:
                return '该功能无过滤设置'
        elif operationType == 'del':
            if function in config['function']['receive']:
                if keyword in config['function']['receive'][function]['filter']:
                    config['function']['receive'][function]['filter'].remove(keyword)
                else:
                    return '该角色不在该功能权限列表中'
            else:
                return '该功能无过滤设置'
        else:
            return '没有这个操作类型'
        with open(configDir, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config))
        return '设置成功'
    except Exception as e:
        print(e)
        return None


def setTellraw(token, tellraw):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            return None
        config['tellraw'] = tellraw
        with open(configDir, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config))
        return True
    except Exception as e:
        print(e)
        return None


def getTellraw(token):
    try:
        configDir = f'serverConfig/{token}.json'
        if os.path.exists(configDir):
            with open(configDir, 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            return None
        return config['tellraw']
    except Exception as e:
        print(e)
        return None