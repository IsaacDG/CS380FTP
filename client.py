import socket               # Import socket module
import time
import binascii
import binhex
import pickle
import getpass
import xor
import sys


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
    sum = sum % 2000000000
    return int.to_bytes(sum, 10, sys.byteorder)


k = open('key', 'rb')
key = k.read()

s = socket.socket()         # Create a socket object
s1 = socket.socket()
host = socket.gethostname() # Get local machine name
port = 12345                 # Reserve a port for your service.
port1 = 12346
s1.bind((host, port1))
s.connect((host, port))

s1.listen(5)

c1, addr1 = s1.accept()

f = open('tosend.png','rb')
print('Sending...')

verified = False
while(not verified):
    user = input('Please enter your username: ')
    passw = input('Please enter your password: ')

    unpass = user + "^" + passw
    s.sendall(unpass.encode('utf-8'))

    time.sleep(0.5)

    verif = c1.recv(128)
    if(verif.decode() == "Connection Verified!"):
        print("HERE")
        verified = True
    else:
        print("Your username or password was incorrect, please try again.")

packet = f.read(128)
pack = {}

while (packet):
    pack['bytes'] = xor.encrypt(packet, key)
    pack['hash'] = xor.encrypt(hashbytes(packet), key)
    a = pickle.dumps(pack)  #pickled dictionary{bytes, hash}
    s.sendall(a)

    msg = c1.recv(1024)
#    print(msg.decode())
    if(msg.decode() == "OK"):
        packet = f.read(128)

f.close()
#print("Done Sending")
s.shutdown(socket.SHUT_WR)
#print(s.recv(128).decode())
c1.close()
s.close                     # Close the socket when done

