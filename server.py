import socket               # Import socket module
import sys
import time
import pickle
import binascii
import binhex
import xor
import pandas as pd
import os



def hashbytes(byts):
	result = 17

	for b in byts:
		result = result * 23 + b.__hash__()

	return int.to_bytes(result, 100, sys.byteorder)

k = open('key', 'rb')               # open file containing bytes for xor
data = pd.read_csv('usepass.csv')   # open table for username and passwords
key = k.read()

s = socket.socket()         # Create a socket object
s1 = socket.socket()
host = socket.gethostname() # Get local machine name
host1 = socket.gethostname()
port = 12345                 # Reserve a port for your service.
fPort = 12346

s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.


c, addr = s.accept()     	# Establish connection with client.


s1.connect((host, fPort))

while True:

	print('Got connection from', addr)

	verified = False
	while (not verified):
		passw = c.recv(128)
		passw = passw.decode()

		time.sleep(0.5)

		info = passw.split('^')

		for u, p in zip(data['username'], data['password']):
			if (u == info[0] and p == info[1]):
				s1.sendall("Connection Verified!".encode())
				verified = True
				break
		if not verified:
			s1.sendall("Incorrect".encode())

	print("Connection verified with sender signed in as " + info[0])

	filepath = c.recv(1024)
	f = open(filepath, 'wb')

	print("Recieving...")
	packet = c.recv(1024)
	retry = 0
	while packet:
		b = pickle.loads(packet)	#load the pickled dictionary
		senthash = xor.decrypt(b['hash'],key)
		rehash = hashbytes(xor.decrypt(b['bytes'], key))

		if senthash == rehash:
			retry = 0
			f.write(xor.decrypt(b['bytes'], key))
			s1.sendall("OK".encode())
		else:
			if retry < 4:
				retry += 1
				s1.sendall("0".encode())
			else:
				s1.sendall("CLOSING".encode())
				print("Hashes were not matching, closing connection.")
				time.sleep(1)
				c.close()
				sys.exit()
		packet = c.recv(1024)

	f.close()
	print("Done Receiving")

	c.close()                # Close the connection
	sys.exit()