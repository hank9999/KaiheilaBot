from khl.hardcoded import API_URL
from config import getBotConfig, getToken, setFunctionSwitch, getFunctionSwitch, setToken, checkAdmin, unsetToken, operationPermission, checkPermission
from khl import TextMsg, Bot, Cert
from config import setChannel, getServerConfig
from serverUtils import getAllStatus, runCommand

botConfig = getBotConfig()

cert = Cert(type=botConfig['type'], client_id=botConfig['client_id'], client_secret=botConfig['client_secret'],
            token=botConfig['token'], verify_token=botConfig['verify_token'], encrypt_key=botConfig['encrypt_key'])
bot = Bot(cmd_prefix=botConfig['cmd_prefix'], cert=cert)


@bot.command(name='hello')
async def hello(msg: TextMsg, *args):
    await msg.reply(f'GuildId: {msg.guild_id}\nChannelId: {msg.channel_id}\nAuthorId: {msg.author_id}')


@bot.command(name='getuserid')
async def getuserid(msg: TextMsg, *args):
    if len(args) == 0:
        await msg.reply(f'{msg.extra["author"]["username"]}: {msg.author_id}')
    else:
        if len(msg.mention) == 0:
            await msg.reply('没有at到用户')
        else:
            message = ''
            for user in args:
                user = user.replace('#', ': ').replace('@', '\n')
                message += user
            message = message[1:]
            if len(msg.mention) != len(args):
                message += '\nPS: 可能有用户没at到'
            await msg.reply(message)


@bot.command(name='listrole')
async def listrole(msg: TextMsg, *args):
    roleData = await bot.get(f'{API_URL}/guild-role/index?compress=0', params={'guild_id': str(msg.guild_id)})
    message = ''
    for i in roleData:
        message += f'{i["name"]}: {i["role_id"]}\n'
    await msg.reply(message)


@bot.command(name='help')
async def help(msg: TextMsg, *args):
    cmd_prefix = ''
    for cp in botConfig['cmd_prefix']:
        cmd_prefix += f'{cp} '
    cmd_prefix = cmd_prefix[:-1]
    message = '帮助:\n' \
              f'支持{cmd_prefix}作为指令前缀\n' \
              'PS: 以下指令均未添加前缀, 复制时请勿复制冒号\n' \
              ' - hello: 获取服务器ID, 频道ID, 用户ID\n' \
              ' - getuserid: 获得自己 或 at到的用户 的ID\n' \
              ' - listrole: 列出当前频道角色ID\n' \
              ' - settoken <token>: 设置服务器的token\n' \
              ' - unsettoken: 解绑token\n' \
              ' - setchannel:\n' \
              '    - setchannel default: 设置默认频道\n' \
              '    - setchannel reset: 恢复所有功能频道至默认\n' \
              '    - setchannel <功能名称>: 设置单个功能频道\n' \
              ' - info: 列出各功能启用情况, 对应频道ID(若为默认频道则不显示频道ID)\n' \
              ' - function <功能名称> true/false: 设置功能开关(true启用, false关闭)\n' \
              ' - status: 列出MC服务器在线情况, 版本, 在线玩家\n' \
              ' - run <服务器名称> <指令>: 远程执行指令 (若指令内含有引号,请在引号前加 \ 进行反义; 原版指令无法获取返回,请开启日志转发功能)\n' \
              ' - permission:\n' \
              '    - permission list: 显示权限对应的角色名称及ID\n' \
              '    - permission add <功能名称> <角色ID>: 给予角色对应权限\n' \
              '    - permission del <功能名称> <角色ID>: 移除角色对应权限\n' \
              '\n' \
              '\n' \
              '功能名称列表:\n' \
              ' - log: 日志转发功能\n' \
              ' - Chat: 聊天消息转发\n' \
              ' - PlayerCommand: 玩家执行指令日志\n' \
              ' - Login: 玩家登陆日志\n' \
              ' - Logout: 玩家退出日志\n' \
              ' - RconCommand: Rcon指令指令日志\n' \
              ' - commandReturn: 远程执行指令返回\n' \
              ' - status: 服务器状态\n' \
              ' - command: 远程执行指令\n'
    await msg.reply(message)


@bot.command(name='settoken')
async def settoken(msg: TextMsg, *args):
    token = getToken(msg.guild_id)
    if token is not None:
        await msg.reply('已配置token, 若需重设, 请先解绑')
    else:
        if len(args) != 1:
            await msg.reply('帮助: .settoken <token>')
        else:
            message = setToken(args[0], msg.guild_id)
            await msg.reply(message)


@bot.command(name='unsettoken')
async def unsettoken(msg: TextMsg, *args):
    token = getToken(msg.guild_id)
    if token is None:
        await msg.reply('未配置token')
    else:
        adminPm = checkAdmin(token, int(msg.author_id))
        if adminPm is None:
            await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试重新配置或联系管理')
        elif not adminPm:
            await msg.reply('您无权使用该指令')
        else:
            message = unsetToken(token, msg.guild_id)
            await msg.reply(message)


@bot.command(name='setchannel')
async def setchannel(msg: TextMsg, *args):
    token = getToken(msg.guild_id)
    if token is None:
        await msg.reply('未配置token')
    else:
        adminPm = checkAdmin(token, int(msg.author_id))
        if adminPm is None:
            await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试重新配置或联系管理')
        elif not adminPm:
            await msg.reply('您无权使用该指令')
        else:
            if len(args) == 0:
                await msg.reply('默认频道: .setchannel default\n恢复所有功能频道至默认: .setchannel reset\n设置单个功能频道: .setchannel <功能名称>')
            elif len(args) == 1:
                message = setChannel(token, msg.channel_id, args[0])
                await msg.reply(message)
            else:
                await msg.reply('参数错误')


@bot.command(name='info')
async def info(msg: TextMsg, *args):
    token = getToken(msg.guild_id)
    if token is None:
        await msg.reply('未配置token')
    else:
        config = getServerConfig(token)
        if config is None:
            await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试重新配置或联系管理')
        else:
            message = ''
            for functionType, function in config['function'].items():
                message += f'{functionType}:\n'
                for key in function.keys():
                    message += f' - {key}: {function[key]["enable"]}\n'
                    if 'channel_id' in function[key]:
                        if function[key]['channel_id'] != -1:
                            message += f'      channel_id: {function[key]["channel_id"]}\n'
            await msg.reply(message)


@bot.command(name='function')
async def function(msg: TextMsg, *args):
    token = getToken(msg.guild_id)
    if token is None:
        await msg.reply('未配置token')
    else:
        adminPm = checkAdmin(token, int(msg.author_id))
        if adminPm is None:
            await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试重新配置或联系管理')
        elif not adminPm:
            await msg.reply('您无权使用该指令')
        else:
            if len(args) != 2:
                await msg.reply('设置功能开关帮助: .function <功能名称> true/false')
            else:
                message = setFunctionSwitch(token, args[0], args[1])
                await msg.reply(message)


@bot.command(name='status')
async def status(msg: TextMsg, *args):
    token = getToken(msg.guild_id)
    if token is None:
        await msg.reply('未配置token')
    else:
        if getFunctionSwitch(token, 'status'):
            hasPermission = checkPermission(token, 'status', msg.author.roles)
            if hasPermission is None:
                await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试联系管理')
            elif not hasPermission:
                await msg.reply('您没有权限执行此指令')
            else:
                data = await getAllStatus(token)
                if data is None:
                    await msg.reply('无服务器在线')
                else:
                    message = ''
                    for server in data:
                        if data[server]['status'] == 'offline':
                            message += f'{server}: 离线\n'
                        else:
                            message += f'{server}: 在线\n    版本: {data[server]["version"]}\n    在线玩家: '
                            if len(data[server]['onlinePlayer']) == 0:
                                message += '无\n'
                            else:
                                onlinePlayers = ''
                                for player in data[server]['onlinePlayer']:
                                    onlinePlayers += f'{player}, '
                                onlinePlayers = onlinePlayers[:-2]
                                message += f'{onlinePlayers}\n'
                    await msg.reply(message)
        else:
            await msg.reply('该功能未启用')


@bot.command(name='run')
async def run(msg: TextMsg, *args):
    token = getToken(msg.guild_id)
    if token is None:
        await msg.reply('未配置token')
    else:
        if getFunctionSwitch(token, 'command'):
            hasPermission = checkPermission(token, 'command', msg.author.roles)
            if hasPermission is None:
                await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试联系管理')
            elif not hasPermission:
                await msg.reply('您没有权限执行此指令')
            else:
                if len(args) < 2:
                    await msg.reply('远程执行指令帮助:\n.run <服务器名称> <指令>(若指令内含有引号 请在引号前加 \ 进行反义)\n原版指令无法获取返回 请开启日志转发功能')
                else:
                    command = ''
                    for i in args[1:]:
                        command += f'{i} '
                    command = command[:-1]
                    success = await runCommand(token, args[0], command)
                    if success == 'offline':
                        await msg.reply('服务器不在线')
                    elif success == 'failure':
                        await msg.reply('指令发送失败')
                    else:
                        await msg.reply(f'指令发送成功 sn: {success}')
        else:
            await msg.reply('该功能未启用')


@bot.command(name='permission')
async def permission(msg: TextMsg, *args):
    token = getToken(msg.guild_id)
    if token is None:
        await msg.reply('未配置token')
    else:
        adminPm = checkAdmin(token, int(msg.author_id))
        if adminPm is None:
            await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试重新配置或联系管理')
        elif not adminPm:
            await msg.reply('您无权使用该指令')
        else:
            if len(args) > 0:
                if args[0] == 'list':
                    config = getServerConfig(token)
                    if config is None:
                        await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试重新配置或联系管理')
                    else:
                        message = ''
                        roleData = await bot.get(f'{API_URL}/guild-role/index?compress=0', json={'guild_id': str(msg.guild_id)})
                        roleIdMapping = {}
                        for i in roleData:
                            roleIdMapping[str(i['role_id'])] = str(i['name'])
                        for function in config['permission']:
                            message += f'{function}: '
                            for roleId in config['permission'][function]:
                                roleId = str(roleId)
                                if roleId not in roleIdMapping:
                                    message += f'{roleId}(角色已被删除), '
                                else:
                                    message += f'{roleId}({roleIdMapping[roleId]}), '
                            if len(config['permission'][function]) != 0:
                                message = message[:-2] + '\n'
                            else:
                                message += '无\n'
                        await msg.reply(message)
                elif args[0] == 'add':
                    if len(args) != 3:
                        await msg.reply('参数错误\n权限添加帮助: .permission add <功能名称> <角色ID>')
                    else:
                        message = operationPermission(token, 'add', args[1], args[2])
                        if message is None:
                            await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试重新配置或联系管理')
                        else:
                            await msg.reply(message)
                elif args[0] == 'del':
                    if len(args) != 3:
                        await msg.reply('参数错误\n权限删除帮助: .permission del <功能名称> <角色ID>')
                    else:
                        message = operationPermission(token, 'del', args[1], args[2])
                        if message is None:
                            await msg.reply('已获取token但未获取到配置文件, 请重试.\n若多次出现请尝试重新配置或联系管理')
                        else:
                            await msg.reply(message)
                else:
                    await msg.reply('未知参数, 请查看帮助 .help permission')


def botRun():
    bot.run()
