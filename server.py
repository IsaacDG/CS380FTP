import socket               # Import socket module
import sys
import time
import pickle
import binascii
import binhex

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
host1 = socket.gethostname()
port = 12345                 # Reserve a port for your service.
fPort = 12346

s.bind((host, port))        # Bind to the port
f = open('torecv.png','wb')
s.listen(5)                 # Now wait for client connection.


c, addr = s.accept()     	# Establish connection with client.
#c1, addr1 = s1.accept()

s1.connect((host, fPort))

while True:
	print("hello")
#	c, addr = s.accept()      #Establish connection with client.
	print('Got connection from', addr)
	passw = c.recv(128)

	time.sleep(0.5)

	if passw.decode("utf-8") == "password":
		print("Connection Verified!")


	print("Recieving...")
	packet = c.recv(1024)

	while(packet):
		b = pickle.loads(packet)
		if (b['hash'] == hashbytes(b['bytes'])):
			f.write(b['bytes'])
			s1.sendall("OK".encode())
		packet = c.recv(1024)


	f.close()
	print("Done Receiving")
	#    c.send('Thank you for connecting')
	c.close()                # Close the connection
	sys.exit()