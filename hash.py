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