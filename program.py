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
from passlib.hash import pbkdf2_sha256


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
	while not verified: # loop to check for verification of password and username
		user = input('Please enter your username: ')
		passw = input('Please enter your password: ')

		unpass = user + "^" + passw         # delimit the username and password
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
		f = open(name + ".asc", 'wb')           # writing ASCII bytes to separate file so as to not overwrite the actual data
		f.write(bytes(ba64.b64_encode(bytearray(dat)).encode()))
		f = open(name + ".asc", 'rb')
		filepath = name + ".asc"
		s.sendall("A".encode())
	else:
		s.sendall("N".encode())

	statinfo = os.stat(filepath)
	totalBytes = statinfo.st_size
	s.sendall(str(totalBytes).encode())  # send total size of file to receiver

	print("Sending your data . . . Please wait.")
	packet = f.read(2048)
	pack = {}

	count = 0       # debugging flag to send bad data
	packCount = 0   # count how many packets we have sent thus far

	while packet:
		if count < 2:
			count += 1
			encrypteddat = xor.encrypt(packet, key)
			test = bytearray(encrypteddat)
			test[0] = 1     # modify the first byte
			pack['bytes'] = test
			encryptedhash = xor.encrypt(hash.hashbytes(packet), key)
			pack['hash'] = encryptedhash
			a = pickle.dumps(pack)
			s.sendall(a)
		else:
			encrypteddat = xor.encrypt(packet, key)                     # encrypt the data with XOR cipher
			encryptedhash = xor.encrypt(hash.hashbytes(packet), key)    # encrypt the hash with XOR cipher
			pack['bytes'] = encrypteddat
			pack['hash'] = encryptedhash
			a = pickle.dumps(pack)                                      # pickled dictionary{bytes, hash}
			s.sendall(a)                                                # send the dictionary

		msg = c1.recv(128)

		if msg.decode() == "OK":  # chunk received and verified.
			packCount += 1
			print("Data sent and hash verified for packet #" + str(packCount))
			packet = f.read(2048)
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


def receiver():
	k = open('key', 'rb')  # open file containing bytes for xor
	data = pd.read_csv('usepass.csv')  # open table for username and passwords
	key = k.read()

	s = socket.socket()  # Create a socket object
	s1 = socket.socket()
	host = socket.gethostname()  # Get local machine name
	port = 12345  # Reserve a port for your service.
	fPort = 12346

	s.bind((host, port))  # Bind to the port

	s.listen(5)  # Now wait for client connection.

	c, addr = s.accept()  # Establish connection with client.

	s1.connect((host, fPort))

	while True:

		print('Got connection from', addr)

		verified = False

		while not verified:
			passw = c.recv(128)
			passw = passw.decode()

			time.sleep(0.5)

			info = passw.split('^')

			for u, p in zip(data['username'], data['hash']):
				if u == info[0] and pbkdf2_sha256.verify(info[1], p):
					s1.sendall("Connection Verified!".encode())
					verified = True
					break
			if not verified:
				s1.sendall("Incorrect".encode())

		print("Connection verified with sender signed in as " + info[0])

		filepath = c.recv(1024)

		asc = c.recv(1024).decode()

		size = c.recv(128).decode()

		f = open(filepath, 'wb')

		print("Recieving...")
		packet = c.recv(3000)   # how many bytes to read in, 3000 arbitrary, just big enough to get pickle
		retry = 0               # keep track of how many times we have retried
		bytesDLd = 0
		while packet:
			b = pickle.loads(packet)  # load the pickled dictionary
			senthash = xor.decrypt(b['hash'], key)
			rehash = hash.hashbytes(xor.decrypt(b['bytes'], key))

			if senthash == rehash:              # check for integrity
				retry = 0                           # retry count back to 0 because we are not retrying
				bytesDLd += len(b['bytes'])
				f.write(xor.decrypt(b['bytes'], key))
				print("Bytes downloaded: " + str(bytesDLd) + " of " + str(size))
				s1.sendall("OK".encode())
			else:
				if retry < 4:                   # we can still retry if retry is less than 4
					retry += 1
					print("Hash did not match, asking sender to try again. . .")
					s1.sendall("0".encode())
				else:
					s1.sendall("CLOSING".encode())  # retried too many times
					print("Hashes were not matching, closing connection.")
					time.sleep(1)
					c.close()
					sys.exit()
			packet = c.recv(3000)

		f.close()
		if asc == "A":  # we sent over ASCII armored data
			print("Decoding ASCII Armored Data . . . ")
			f = open(filepath, 'rb')            # read the ASCII data that we wrote
			dat = base64.b64decode(f.read())    # decoding the ASCII data we wrote
			trueF = open(filepath, 'wb')        # the true, de-ASCII'd data
			trueF.write(dat)
			trueF.close()
		print("Done Receiving")

		c.close()  # Close the connection
		sys.exit()


def main():
	i = input('Are you the receiver(0) or sender(1)? ')

	if i == "0":
		receiver()
	else:
		sender()

if __name__ == "__main__":
	main()
