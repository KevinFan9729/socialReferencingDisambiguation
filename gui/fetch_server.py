# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 11:13:56 2022

@author: kevei
"""

import socket
import time
# HEADERSIZE = 10
# #server scoket with fixed len header 
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((socket.gethostname(), 1234))#(ip and port)
# s.listen(5)#queue

# while True:
#     clientsocket, address = s.accept() #get client scoket info
#     print(f"connect from {address} has been established!")
#     msg = "welcome to the server"
#     #fixed len header
#     msg = f'{len(msg):<{HEADERSIZE}}' +msg #10 characters long
#     clientsocket.send(bytes(msg,"utf-8")) #this send data to the client socket, but the notation kinda odd, remeber this is the server SEND to the client 
    

#basic socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))#(ip and port)
s.listen(5)#queue


clientsocket, address = s.accept() #get client scoket info
print(f"connect from {address} has been established!")
# time.sleep(10)
clientsocket.send(("Fetch is ready").encode()) #this send data to the client socket, but the notation kinda odd, remeber this is the server SEND to the client 

# while True:
msg=""
msg = clientsocket.recv(1024)#recive from the client
print("from User UI:")
print(msg.decode())
    # clientsocket.close()
    # if msg!="":
    #     break
msg = msg.decode()
clientsocket.send(msg.encode())
msg = clientsocket.recv(1024)#recive from the client
print("from User UI:")
print(msg.decode())
clientsocket.close()