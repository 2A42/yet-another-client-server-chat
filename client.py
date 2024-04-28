import asyncio
import websockets
import colorama

from colorama import Fore, Style
from services import call_createTSV
from services import getDataFromJSON
from myGrpc import send_file

colorama.init()
username = ''
isChatting = False
config = getDataFromJSON('config')
in_file = config['IN_FILE']
HOST = config['IP'] # The server's hostname or IP address
PORT = int(config['NGINX_PORT']) # The port used by the server nginx
GRPC_PORT = config['MYPORT'] # The port used by the server grpc

async def send_data(websocket):
    global isChatting
    print("\nWrite your thoughts here . . ."  + Fore.CYAN)
    while isChatting:
        await asyncio.sleep(0.1)
        message = await asyncio.to_thread(input, ">") #give a separate thread for blocking func input()
        if(message == '/e' or message == 'EXIT'): isChatting = False
        await websocket.send(username + ':' + message)

async def receive_data(websocket):
    while isChatting:
        response = await websocket.recv()
        response = response.split(":", 1)
        name, message = response[0], response[1] 
        if(username != name):
            print(Fore.LIGHTGREEN_EX + '\n' + '@' + name + ': ' + Fore.YELLOW + message + Fore.CYAN)

async def main():
    global username, config, in_file, isChatting, HOST, PORT, GRPC_PORT
    username = input("Enter your username-> ")
    while True:
        try:
            async with websockets.connect(f"ws://{HOST}:{PORT}", open_timeout=30) as client:
                while True:
                        print(Style.RESET_ALL)
                        user = input("========Chatcat.com|\/|ander========\n1. Enter to Chatcat\n2. Create TSV+XLSX\n3. Exit\n")
                        if user == '1':
                            isChatting = True
                            task1 = asyncio.create_task(send_data(client))
                            task2 = asyncio.create_task(receive_data(client))
                            await asyncio.gather(task1, task2) #!!!!!!!!!!!!!!!!!!!!!!
                        elif user == '2':
                            result = send_file(username, HOST, GRPC_PORT, in_file)
                            print(Fore.LIGHTMAGENTA_EX + str(result))
                        elif user == '3':
                            return
        except Exception as e:
                        print(Fore.RED + "Failed! Trying to resolve problem . . .")
                        print("\n" + str(e) + Style.RESET_ALL)

                        # Refresh config data
                        config = getDataFromJSON('config')
                        in_file = config['IN_FILE']
                        HOST = config['IP'] # The server's hostname or IP address
                        PORT = int(config['NGINX_PORT']) # The port used by the server nginx
                        GRPC_PORT = config['MYPORT'] # The port used by the server grpc
                        await asyncio.sleep(1)

asyncio.run(main())
end = input("Put anything to continue . . .")

