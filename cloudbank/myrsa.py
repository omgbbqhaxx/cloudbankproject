from Crypto.PublicKey import RSA
from Crypto import Random
import base64
from Crypto.Hash import SHA256


def instantwallet():
    new_key = RSA.generate(1024, Random.new().read)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    keys = []
    wallet_id = SHA256.new(public_key).hexdigest()
    keys.append(private_key)
    keys.append(public_key)
    keys.append(wallet_id)
    private_key = keys[0]
    public_key =  keys[1]

    # print(private_key)
    # print("-*-*-*-*-*-*-*-*-**-*-----------*-*-*-*-*-*-*-*-*-*")
    # print(public_key)
    # print("-*-*-*-*-*-*-*-*-**-*-----------*-*-*-*-*-*-*-*-*-*")
    # print(wallet_id)
    return keys






#x = key.decrypt(enc_data)
#print(x)
