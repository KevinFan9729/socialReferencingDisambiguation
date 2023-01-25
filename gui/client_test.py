import socket
import time
# host = "kd-pc29.local"
host = socket.gethostname()
port = 8200
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))#(ip and port)
msg = s.recv(1024).decode()
print("speech: "+msg)

print("wait...")
time.sleep(5)
lbl=msg+"|c"
print("send...")
s.send(lbl.encode())
time.sleep(5)


