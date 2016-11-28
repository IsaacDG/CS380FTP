import passlib
from passlib.hash import pbkdf2_sha256

hash = pbkdf2_sha256.encrypt("presentation", rounds = 10000, salt_size=16)
print(hash)

print(pbkdf2_sha256.verify("presentation", hash))