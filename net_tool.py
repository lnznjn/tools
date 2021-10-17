#! /usr/bin/python3 
#Time: 2021/10/15 13:45
#-*- encoding: utf-8 -*-

import socket
import sys
import os
import threading
import getopt

listen  = False
command = False
execute = False
upload  = False
target  = ""
port    = 0

#--------------------------------------------------------------------------------------------------------------------------------------------

def get_help():
    print("Usage: netcat.py -t [host] -p [port]")
    print("-l --listen              - listen on [host]:[port] for incoming connections")
    print("-c --command             - initialize a command shell")
    print("-e --execute=file_to_run - execute the given upon receiving a connection")
    print("-u --upload              - upon receiving connection upload a file an write to [destination]")
    sys.exit(0)

#--------------------------------------------------------------------------------------------------------------------------------------------

def client_send():
    client = socket.socket()

    try:
        client.connect((target, port))

        while True:
            data = input("SHELL> ")
            client.send(data)
            ret = client.recv(2048)
            response = ret
            print(response)     

    except:
        
        print("[-] Exception!")
        client.close()

#--------------------------------------------------------------------------------------------------------------------------------------------

def server_loop():
    global target

    if len(target) == 0:
        
        target = "0.0.0.0"

    try:
        
        server = socket.socket()
        server.bind((target, port))
        server.listen(5)

    except socket.error as e:
        print(e)

    client_socket, addr = server.accept()

    client_handle_thread = threading.Thread(target=client_handle, args=(client_socket, addr,))
    client_handle_thread.start()

#--------------------------------------------------------------------------------------------------------------------------------------------

def run_cmd(cmd_buffer):
    cmd_buffer = cmd_buffer.rstrip()
    
    try:

        output = os.popen(cmd_buffer, "r").read()

    except:
        
        output = "Failed to execute command.\n"

    return output

#--------------------------------------------------------------------------------------------------------------------------------------------

def client_handle(client_socket, addr):
    global command
    global execute
    global upload

    print("[+] a connection from {}.".format(addr))
    if upload:
        
        file_buffer = ""

        while True:
            
            data = client_socket.recv(2048)

            if not data:
                break

            else:
                file_buffer += data

        try:
            
            with open("text.txt", "wb") as file_file:
                
                file_file.write(file_buffer)
                file_file.close()
            
            client_socket("Successfully saved file to text.txt")
        
        except:
            
            client_socket("Failed to saved file to text.txt")

    if execute:
        
        output = run_cmd(client_socket.recv(1024))
        client_socket.send(output)

    if command:
        print("[*] give shell to {}".format(addr))

        while True:

            cmd_buffer = client_socket.recv(1024)

            ret = run_cmd(cmd_buffer)

            client_socket.send(ret)

#--------------------------------------------------------------------------------------------------------------------------------------------

def main():
    global listen
    global command
    global execute
    global upload
    global target
    global port

    if not sys.argv[1:]:
        
        get_help()


    try:
        
        opts, args = getopt.getopt(sys.argv[1:],
                "hlecut:p:",
                ["help", "listen", "command", "upload", "execute", "target=", "port="])

    except getopt.GetoptError as err:
        
        print("[-] ", err)

    for o, a in opts:
        if o in ("-h", "--help"):
            get_help()

        elif o in ("-l", "--listen"):
            listen = True

        elif o in ("-c", "--command"):
            command = True

        elif o in ("-e", "--execute"):
            execute = True

        elif o in ("-u", "--upload"):
            upload = True

        elif o in ("-t", "--target"):
            target = a

        elif o in ("-p", "--port"):
            port = int(a)

        else:
            print("[-] unhandled Option")

    if not listen and len(target) and port > 0:

        client_send()

    elif listen:
        print("[*] start listening...")
        server_loop()

main()
