import socket               # Import socket module
import time
import binascii
import binhex
import pickle

def hashbytes(byts):
    sum = 17
    i = 0
    for byte in byts:
        if(i%2 == 0):
            sum *= (byte + 17)
        else:
            sum += byte
        i += 1
    sum *= len(byts) * 17
    return sum % 2000000000

s = socket.socket()         # Create a socket object
s1 = socket.socket()
host = socket.gethostname() # Get local machine name
port = 12345                 # Reserve a port for your service.
port1 = 12346
s1.bind((host, port1))
s.connect((host, port))

s1.listen(5)

c1, addr1 = s1.accept()

passw = "password"
f = open('tosend.png','rb')
print('Sending...')

s.sendall(passw.encode('utf-8'))

time.sleep(0.5)

packet = f.read(128)
pack = {}

while (packet):
    pack['bytes'] = packet
    pack['hash'] = hashbytes(packet)
    a = pickle.dumps(pack)
    s.sendall(a)
#    hash = hashbytes(packet)
#    info = packet.decode('utf-16-le') + "^" + str(hash)
#    s.sendall(info.encode())
    msg = c1.recv(1024)
    print(msg.decode())
    if(msg.decode() == "OK"):
        packet = f.read(128)

f.close()
#print("Done Sending")
s.shutdown(socket.SHUT_WR)
#print(s.recv(128).decode())
c1.close()
s.close                     # Close the socket when done

