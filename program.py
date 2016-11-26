import sys
import socket
import time
import base64
import pandas as pd
import pickle
import xor
import hash
import ba64
import os

def sender():
	k = open('key', 'rb')
	key = k.read()

	s = socket.socket()  # Create a socket object
	s1 = socket.socket()
	host = socket.gethostname()  # Get local machine name
	port = 12345  # Reserve a port for your service.
	port1 = 12346
	s1.bind((host, port1))
	s.connect((host, port))

	s1.listen(5)

	c1, addr1 = s1.accept()

	filepath = input('Enter name of file to send: ')
	while not os.path.isfile(filepath):
		filepath = input('Please enter a valid path to file: ')

	f = open(filepath, 'rb')

	verified = False
	while not verified:
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

	ans = input("Would you like to ascii armor your data?(y/n): ")
	if ans == 'y':
		print("ASCII Armoring . . .")
		dat = f.read()
		f = open(name + ".asc", 'wb')
		f.write(bytes(ba64.b64_encode(bytearray(dat)).encode()))
		f = open(name + ".asc", 'rb')
		s.sendall("A".encode())
	else:
		s.sendall("N".encode())

	print("Sending your data . . . Please wait.")
	packet = f.read(128)
	pack = {}

	test = False
	count = 0

	while packet:
		if count < 2:
			count += 1
			encrypteddat = xor.encrypt(packet, key)
			test = bytearray(encrypteddat)
			test[0] = 1
			pack['bytes'] = test
			encryptedhash = xor.encrypt(hash.hashbytes(packet), key)
			pack['hash'] = encryptedhash
			a = pickle.dumps(pack)
			test = True
			s.sendall(a)
		else:
			encrypteddat = xor.encrypt(packet, key)
			# test = bytearray(encrypteddat)
			# test[0] = 1
			encryptedhash = xor.encrypt(hash.hashbytes(packet), key)
			pack['bytes'] = encrypteddat
			pack['hash'] = encryptedhash
			a = pickle.dumps(pack)  # pickled dictionary{bytes, hash}
			s.sendall(a)

		msg = c1.recv(1024)

		if msg.decode() == "OK":  # chunk received and verified.
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
	s.close  # Close the socket when done

def receiver():
	k = open('key', 'rb')  # open file containing bytes for xor
	data = pd.read_csv('usepass.csv')  # open table for username and passwords
	key = k.read()

	s = socket.socket()  # Create a socket object
	s1 = socket.socket()
	host = socket.gethostname()  # Get local machine name
	host1 = socket.gethostname()
	port = 12345  # Reserve a port for your service.
	fPort = 12346

	s.bind((host, port))  # Bind to the port

	s.listen(5)  # Now wait for client connection.

	c, addr = s.accept()  # Establish connection with client.

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

		asc = c.recv(1024).decode()

		f = open(filepath, 'wb')

		print("Recieving...")
		packet = c.recv(1024)
		retry = 0
		while packet:
			b = pickle.loads(packet)  # load the pickled dictionary
			senthash = xor.decrypt(b['hash'], key)
			rehash = hash.hashbytes(xor.decrypt(b['bytes'], key))

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
		if asc == "A":
			print("Decoding ASCII Armored Data . . . ")
			f = open(filepath, 'rb')
			dat = base64.b64decode(f.read())
			trueF = open(filepath, 'wb')
			trueF.write(dat)
			trueF.close()
		print("Done Receiving")

		c.close()  # Close the connection
		sys.exit()



def main():
	i = input('Are you the receiver(0) or sender(1)? ')

	if i == "0":
		print("HERE")
		receiver()
	else:
		print("HERE1")
		sender()

if __name__ == "__main__":
	main()