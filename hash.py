import sys
def hashbytes(byts):
	result = 17

	for b in byts:
		result = result * 23 + b.__hash__()

	return int.to_bytes(result, 1000, sys.byteorder)