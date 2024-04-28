# echo-server.py
import asyncio
import websockets
import colorama

from colorama import Fore, Style
from rabbitmq import *
from services import getDataFromJSON
from services import reload_nginx

colorama.init()
config = getDataFromJSON('config')
output_file = config['OUT_FILE']
HOST = config['IP']
NGINX_PORT = int(config['NGINX_PORT'])  # (ID of Process) Port to listen on (non-privileged ports are > 1023)

connected = set() # Список подключенных клиентов
clearChat = False

async def receiver(websocket, path):
        connected.add(websocket)
        global clearChat
        try:
            async for message in websocket:
                    print(Fore.CYAN + message + Style.RESET_ALL)
                    content = message.split(":", 1)
                    name, msg = content[0], content[1]
                    if(msg == '/clear' or msg == 'CLEARQ'): clearChat = True
                    queue_send(message)
        except Exception as e:
                   print(Fore.RED + "\nRaised Exception!")
                   print(str(e) + Style.RESET_ALL)
        finally:
            connected.remove(websocket)

async def sender():
        lastMessageIdx = None
        global clearChat
        while True:
            await asyncio.sleep(5)
            response = queue_consume(clearChat)
            clearChat = False
            if(lastMessageIdx != len(response)):
                print("[LOG] queue size: " + str(len(response)))
                newMessages = response[lastMessageIdx:]
                lastMessageIdx = len(response)
                for msg in newMessages:
                    for conn in connected:
                        try:
                            await conn.send(msg)
                        except Exception as e:
                            print(Fore.RED + "\nRaised Exception!")
                            print(e)

async def start_server():
        server = await websockets.serve(receiver, HOST, None, ping_timeout=600)
        
        PORT = server.sockets[0].getsockname()[1]
        print(f"Server is listening on {HOST}:{PORT} . . .")

        # Перезапускаем Nginx
        s = f"{HOST}:{PORT}"
        backend_servers = []

        with open("backend_servers.txt", "r") as servers_file:
            backend_servers = [line.strip() for line in servers_file]
        backend_servers.insert(0, s)
        backend_servers = map (lambda x: x + '\n', backend_servers)
        with open("backend_servers.txt", 'w') as f: f.writelines(backend_servers)
        reload_nginx(HOST, NGINX_PORT)

        # Запускаем поток сервера
        await server.wait_closed()

async def main():
        task1 = asyncio.create_task(start_server()) 
        task2 = asyncio.create_task(sender())
        await asyncio.gather(task1, task2)

asyncio.run(main())