import binascii
import base64
import re

# f = open('tosend.png', 'rb')


def rshift(val, n): return (val % 0x100000000) >> n


def b64_encode(s):
	b64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
	r = ""
	p = ""
	c = len(s) % 3

	if c > 0:
		while c < 3:
			p += '='
			s.append(ord('\0'))
			c += 1


	for i in range(0, len(s), 3):
		# if (i > 0) and (i / 3 * 4) % 76 == 0:
		# 	r += "\r\n"

		n = (s[i] << 16) + (s[i+1] << 8) + s[i+2]

		n = [rshift(n, 18) & 63, rshift(n, 12) & 63, rshift(n, 6) & 63, n & 63]

		r += b64chars[n[0]] + b64chars[n[1]] + b64chars[n[2]] + b64chars[n[3]]

	return (r[0:len(r)-len(p)] + p)

# def b64_decode(s):
# 	b64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
# 	s = str(s)
# 	s = re.sub(r'')
# 	s = s.replace(str(re.compile('[^'+b64chars.join("")+'=]')), "")

#print(base64.b64encode(f.read()))
# data = f.read()
# thing = str(base64.b64encode(data))
# mine = b64_encode(bytearray(data))
# print(base64.b64decode(mine))
# print(data)
# if b64_encode(bytearray(data)) == thing[2:len(thing) - 1]:
# 	print("TRUE")
#print(base64.b64encode(data))
#print(base64.b64encode(data))
#if(base64.b64encode(data) == b64_encode(bytearray(data))):
#	print("TRUE")
#b64_encode(bytearray(f.read()))
#print(bytes.fromhex(bts[4*2:8*2].decode("ascii")).decode("ascii"))