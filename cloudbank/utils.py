#-*- coding: utf-8 -*-
from ecdsa import SigningKey, SECP256k1, NIST384p, BadSignatureError, VerifyingKey
import hashlib, arrow
from django.conf import settings
from django.db.models import Avg, Sum, Count
from core.models import transaction


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


def checkreward(wallet):
   #settings.REWARD_HASH
   utc = arrow.utcnow()
   local = utc.to('GMT')
   first_timestamp = local.timestamp

   tenminutes = utc.shift(minutes=-10)
   tenlocal = tenminutes.to('GMT')
   tmago = tenlocal.timestamp
   checklastreward = transaction.objects.filter(sender=settings.REWARD_HASH,receiver=settings.NODE_OWNER_WALLET)
   if not checklastreward:
       addzeroward(wallet)
   else:
       if (checklastreward[0].first_timestamp > tmago):
           print("10 dakika geçmiş demektir")
           addreward(wallet)
       else:
           print("daha on dakika dolmamış demektir.")

       return "utils works correctly"





def addreward(wallet):

    utc = arrow.utcnow()
    local = utc.to('GMT')
    first_timestamp = local.timestamp

    newtrans = transaction(sender=settings.REWARD_HASH,
    senderwallet=settings.REWARD_HASH,
    receiver=wallet,
    prevblockhash=transaction.objects.all().last().blockhash,
    blockhash=settings.REWARD_HASH,
    amount=100,
    nonce=0,
    first_timestamp=first_timestamp,
    P2PKH=settings.REWARD_HASH,
    verification=True
    ).save()

def addzeroward(wallet):

    utc = arrow.utcnow()
    local = utc.to('GMT')
    first_timestamp = local.timestamp

    newtrans = transaction(sender=settings.REWARD_HASH,
    senderwallet=settings.REWARD_HASH,
    receiver=wallet,
    prevblockhash=transaction.objects.all().last().blockhash,
    blockhash=settings.REWARD_HASH,
    amount=100,
    nonce=0,
    first_timestamp=first_timestamp,
    P2PKH=settings.REWARD_HASH,
    verification=True
    ).save()
