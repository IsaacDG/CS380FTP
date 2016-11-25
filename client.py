import socket               # Import socket module
import time
import binascii
import binhex
import pickle
import getpass
import xor
import sys
import os


def hashbytes(byts):
    result = 17

    for b in byts:
        result = result * 23 + b.__hash__()

    return int.to_bytes(result, 100, sys.byteorder)
    # i = 0
    # for byte in byts:
    #     if(i%2 == 0):
    #         sum *= (byte + 17)
    #     else:
    #         sum += byte
    #     i += 1
    # sum *= len(byts) * 17
    # sum = sum % 2000000000
    # return int.to_bytes(sum, 10, sys.byteorder)


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

filepath = input('Enter name of file to send: ')
while not os.path.isfile(filepath):
    filepath = input('Please enter a valid path to file: ')

f = open(filepath, 'rb')

#f = open('tosend.png','rb')

verified = False
while(not verified):
    user = input('Please enter your username: ')
    passw = input('Please enter your password: ')

    unpass = user + "^" + passw
    s.sendall(unpass.encode('utf-8'))

    time.sleep(0.5)

    verif = c1.recv(128)
    if verif.decode() == "Connection Verified!":
        print("Verified. Signed in as " + user)
        verified = True
    else:
        print("Your username or password was incorrect, please try again.")

name, ext = os.path.splitext(filepath)
s.sendall(("torecv" + ext).encode())

print("Sending your data . . . Please wait.")
packet = f.read(128)
pack = {}

test = False

while packet:
    if not test:
        encrypteddat = xor.encrypt(packet, key)
        test = bytearray(encrypteddat)
        test[0] = 1
        pack['bytes'] = test
        encryptedhash = xor.encrypt(hashbytes(packet), key)
        pack['hash'] = encryptedhash
        a = pickle.dumps(pack)
        test = True
        s.sendall(a)
    else:
        encrypteddat = xor.encrypt(packet, key)
        test = bytearray(encrypteddat)
        test[0] = 1
        encryptedhash = xor.encrypt(hashbytes(packet), key)
        pack['bytes'] = test
        pack['hash'] = encryptedhash
        a = pickle.dumps(pack)  #pickled dictionary{bytes, hash}
        s.sendall(a)

    msg = c1.recv(1024)

    if msg.decode() == "OK":    #chunk received and verified.
        packet = f.read(128)
    elif msg.decode() == "0":
        print("Hashes did not match, retrying")
        packet = packet
    elif msg.decode() == "CLOSING":
        print("Too many retries, closing connection.")
        f.close()
        c1.close()
        s.close()
        sys.exit()

f.close()
print("The data was sent successfully.")
s.shutdown(socket.SHUT_WR)
c1.close()
s.close                     # Close the socket when done

