from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import json
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

cleartextPublicKeyPEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDCEx0s0PeZH7Pmpb5klJKVGiIB
gz8xC9ADBzzFlaw5zMkeCNBtOJfCkdt0s59mAgrlo6DdRlwuC+OytyMFauEq+yjf
TUx0hO1/fj9pg6bBh8eilgArR0Qsca/QMbL2qMzZoL8kwTZT6KT+/me+gqsA0AX/
5/U8sMrvJS520j49DwIDAQAB
-----END PUBLIC KEY-----"""

private = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDCEx0s0PeZH7Pmpb5klJKVGiIBgz8xC9ADBzzFlaw5zMkeCNBt
OJfCkdt0s59mAgrlo6DdRlwuC+OytyMFauEq+yjfTUx0hO1/fj9pg6bBh8eilgAr
R0Qsca/QMbL2qMzZoL8kwTZT6KT+/me+gqsA0AX/5/U8sMrvJS520j49DwIDAQAB
AoGBAMBvIXOptIiRZdmiqLmkk//iDKwBTqw8MUJ/b6PfOAmL5DOyu7BA+EHGTJtX
7ArCpblz2PLvbEGAKoOvkbsychZpMCEmw2cQe+62sHTEmCCDnLKPMXxpwykieGkb
dPuP7DMxWwQubQkVe5P27L+jcYg9MBn3S/Ct7ziAXYpChXrJAkEA3cRlAKiA/a4D
cr1wJg0jLJ5Bzkjtb3tchciyHM4VWl1MMQ/OPkEWazA1BjllhpvQ7w3jNxeQ7FbU
BA7m8sMkiwJBAOAIZAmotPk7trOX5UMfh4QVkM+ULoBld2wZf1Uafhk52VAIwiMA
vtVW+BtXloHD13A0Lkt+ydSE6P48KAQSZg0CQGvzlC8T12aldGxAJv1+26Z2ixX9
jgb8h/df0MQQ1Xgdfl9LkFvhlyYqW0ViXzd9VeFoYziIMjW5to8bKfT2ZS0CQF+p
NY4qS5xgsxLcuTiALg1oZ/06+OA6c1PlT0m3lkCPQwu5savglZvjFu4V6F5gkY2H
unziFqx4VES6yxtx/8ECQDIVZpWU/ib32kRyP+YGz+HqsHW4Kfs0IQTg9IWP509
ncXE16hy2fgCGWQ6BRnTxdTGAvlgVAb7Vb/jX80p7NPA=
-----END RSA PRIVATE KEY-----"""


rsakey = RSA.importKey(cleartextPublicKeyPEM)
rsakey = RSA.importKey(private)

PlainText = 'Hello Word'

hashA = SHA256.new(PlainText).hexdigest()

digitalSignature = rsakey.sign(hashA,'')

print("HASHS A : " + repr(hashA) + "\n")
print("digitalSign : " + repr(digitalSignature) + "\n")


hashsB = SHA256.new(PlainText).hexdigest()
print("HASHS A : " + repr(hashsB) + "\n")

twitter = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDCEx0s0PeZH7Pmpb5klJKVGiIB
gz8xC9ADBzzFlaw5zMkeCNBtOJfCkdt0s59mAgrlo6DdRlwuC+OytyMFauEq+yjf
TUx0hO1/fj9pg6bBh8eilgArR0Qsca/QMbL2qMzZoL8kwTZT6KT+/me+gqsA0AX/
5/U8sMrvJS520j49DwIDAQAB
-----END PUBLIC KEY-----"""

joker = base64.b64encode(twitter)

newkey = RSA.importKey(base64.b64decode(joker))

print digitalSignature
x = json.dumps(digitalSignature)

#print(x)


print type(x)

if(newkey.verify(hashsB, json.loads(x))):
    print "Match"
else:
    print "failift"
