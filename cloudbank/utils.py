#-*- coding: utf-8 -*-
from ecdsa import SigningKey, SECP256k1, NIST384p, BadSignatureError, VerifyingKey
import hashlib
from django.conf import settings

def instantwallet():
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key() #public_key
    public_key  =  vk.to_string().hex()
    private_key =  sk.to_string().hex()
    keys = []
    wallet_id = generate_wallet_from_pkey(public_key)
    keys.append(private_key)
    keys.append(wallet_id)
    keys.append(public_key)
    return keys


def generate_wallet_from_pkey(public_key):
    binmnmn = public_key.encode('utf-8')
    first_step = 34 - len(settings.CURRENCY)
    wallet_id = hashlib.sha256(binmnmn).hexdigest()
    wallet_id = wallet_id[-first_step:]
    wallet_id = "".join((settings.CURRENCY, wallet_id))
    return wallet_id

def generate_pubkey_from_prikey(private_key):
    try:
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        vk = sk.get_verifying_key() #public_key
        print(vk.to_string().hex())
    except UnicodeDecodeError:
        return  "Check your wallet details"
    return vk.to_string().hex()
