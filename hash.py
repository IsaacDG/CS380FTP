import binascii
import binhex
import array
import pickle

def main():
	info = "hello^motherfucker".split('^')
	f = open('tosend.png', 'rb')
	data = f.read(64)
	datastr = data.decode('utf-16-le') + "^"
	print(datastr)
	if(datastr.encode('utf-16-le') == data):
		print("TRUE")
	test = bytearray.fromhex(datastr)
	if(test == data):
		print("true")

	print(array.array('B',datastr.decode()))
	print(str(data))

	print( str(data) + "^" + str(stuff))

def hashbytes(byts):
	sum = 17
	i = 0
	for byte in byts:
		if(i%2 == 0):
			sum *= byte + 17
		else:
			sum += byte
		i += 1
	sum *= len(byts) * 17
	return sum % 2000000000
if __name__ == "__main__":main()