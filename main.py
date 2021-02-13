from serverWs import serverWsRun
from khlBot import botRun
from config import createMapping


if __name__ == '__main__':
    createMapping()
    serverWsRun()
    botRun()
