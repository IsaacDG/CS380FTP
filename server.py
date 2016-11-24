import socket               # Import socket module
import sys
import time
import pickle
import binascii
import binhex
import xor


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
host1 = socket.gethostname()
port = 12345                 # Reserve a port for your service.
fPort = 12346

s.bind((host, port))        # Bind to the port
f = open('torecv.png','wb')
s.listen(5)                 # Now wait for client connection.


c, addr = s.accept()     	# Establish connection with client.


s1.connect((host, fPort))

while True:
	print("hello")

	print('Got connection from', addr)
	verified = False
	while(not verified):
		passw = c.recv(128)
		passw = passw.decode()

		time.sleep(0.5)

		info = passw.split('^')
		if (info[0] == "isaac" and info[1] == "pass"):
			s1.sendall("Connection Verified!".encode())
			verified = True
		else:
			s1.sendall("Incorrect".encode())

	print("Recieving...")
	packet = c.recv(1024)

	while(packet):
		b = pickle.loads(packet)	#load the pickled dictionary
		if (xor.decrypt(b['hash'],key)  == hashbytes(xor.decrypt(b['bytes'], key))):
			f.write(xor.decrypt(b['bytes'], key))
			s1.sendall("OK".encode())
		packet = c.recv(1024)


	f.close()
	print("Done Receiving")

	c.close()                # Close the connection
	sys.exit()