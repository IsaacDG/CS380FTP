file = open('tosend.png', 'rb')
file1 = open('key', 'rb')
bts = file1.read()

#print(ord('a'))

buffer = file.read(8)


# for bt in buffer:
#     print(bt)

stuff = []
#print(buffer)
def encrypt(buffer, key):
    encrypted = bytearray()
    for i, b in enumerate(buffer):
        encrypted.append(b ^ key[i % len(key)])
        i += 1
    return bytes(encrypted)

def decrypt(encrypted, key):
    decrypted = bytearray()
    for i, b in enumerate(encrypted):
        decrypted.append(b ^ key[i % len(key)])
        i+=1
    return bytes(decrypted)


encrypted = encrypt(buffer, bts)
# print(encrypted)
# print(decrypt(encrypted, bts))
i = 0
for b in buffer:
    stuff.append(b ^ bts[i % len(bts)])
    i+=1

#print(stuff) #encrypted

j = 0
# for thing in stuff:
#     print(thing ^ bts[j % len(bts)], )
#     j+=1


# j = 0
# for thing in stuff:
#     print(thing ^ bts[j])
#     j += 1
# print(stuff)
#
# for b in buffer:
#     print(b)
# print(buffer)
# frame = bytearray()
# frame.append(0xFF)
# frame.append(0xFF)
# frame.append(0xFF)
# frame.append(0xFF)
# frame.append(0xFF)
# frame.append(0xFF)
# frame.append(0xFF)
# frame.append(0xFF)
# print(frame)
# for b, fr in zip(buffer, frame):
#     print(b ^ fr)