import sys
def hashbytes(byts):
	result = 17

	for b in byts:
		result = result * 23 + b.__hash__()

	result = result % sys.maxsize
	return result.to_bytes(64, sys.byteorder)
	# return int.to_bytes(result, 1000, sys.byteorder)