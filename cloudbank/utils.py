#-*- coding: utf-8 -*-
import uuid , json , string , random, urllib, base64, os, sys, time, pickle, collections, math, arrow ,hashlib, websocket ,bson
from ecdsa import SigningKey, SECP256k1, NIST384p, BadSignatureError, VerifyingKey
from django.conf import settings
from django.db.models import Avg, Sum, Count
from core.models import transaction
from datetime import datetime
from django.template.defaultfilters import stringfilter
import netifaces as ni
ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

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


def checkreward():
    checktime = addreward()
    if checktime:
       checklastreward = transaction.objects.filter(sender=settings.REWARD_HASH,receiver=settings.NODE_OWNER_WALLET).last()
       if not checklastreward:
            addreward()
            return "node has been added to network"
       else:
           registerd_time = checklastreward.first_timestamp
           oldtime = arrow.get(registerd_time).shift(minutes=+settings.REWARD_TIME).to("GMT").timestamp
           lasttime = arrow.utcnow().to("GMT").timestamp
           if (oldtime < lasttime):
               addreward()
               return  "congratulations you can earn your coins " + str(oldtime) + " and " + str(lasttime)
           else:
               return "you need waitv" + str(oldtime) + " and " + str(lasttime)

           return "utils works correctly " + str(oldtime) + " and " + str(lasttime)
    else:
        return "wait"


def addreward():
    utc = arrow.utcnow()
    local = utc.to('GMT')
    first_timestamp = local.timestamp
    nonce = miner(first_timestamp, settings.REWARD_HASH, settings.NODE_OWNER_WALLET, 100)
    blockhash = gethash(settings.REWARD_HASH, settings.NODE_OWNER_WALLET, 100, first_timestamp, nonce)
    newtrans = transaction(sender=settings.REWARD_HASH,
    senderwallet=settings.REWARD_HASH,
    receiver=settings.NODE_OWNER_WALLET,
    prevblockhash=transaction.objects.all().last().blockhash,
    blockhash=blockhash,
    amount=100,
    nonce=nonce,
    first_timestamp=first_timestamp,
    P2PKH="reward",
    verification=True
    ).save()

    ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    geturl = "http://{}/api/v1/gettransaction/{}/".format(ip,newtrans.id)
    test = {"server":False,
    "sender":settings.REWARD_HASH,
    "receiver":settings.NODE_OWNER_WALLET,
    "prevblockhash":transaction.objects.all().last().blockhash,
    "blockhash":blockhash,
    "amount":100,
    "nonce":nonce,
    "timestamp":first_timestamp,
    "P2PKH":"reward",
    "verification":True,
    "block" : transaction.objects.all().last().id + 1,
    "message":"new_transaction",
    "url":geturl}

    payload = json.dumps(test)

    ws = websocket.WebSocket()
    wsip = "ws://{}:9000".format(ip)
    ws.connect(wsip)
    ws.send(payload)




def miner(first_timestamp, senderwalletid, receiverhex,amount):
    data = {}
    for nonce in range(0,10000000):
        data['sender'] = str(senderwalletid)                                        #1
        data['receiver'] = str(receiverhex)                                         #2
        data['previous_hash'] =  str(transaction.objects.all().last().blockhash)    #3
        data['amount'] = str(amount)                                                #4
        data['timestamp'] =  str(first_timestamp)                                   #5
        data["nonce"] = str(nonce)
        data = collections.OrderedDict(sorted(data.items()))
        datashash  = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()
        last2char = datashash[-2:]
        if last2char == "01":
            return(nonce)
        else:
            # print(nonce)
            continue

def gethash(senderwalletid, receiverhex, amount, first_timestamp, nonce):
    data = {}
    data['sender'] = str(senderwalletid)                                        #1
    data['receiver'] = str(receiverhex)                                         #2
    data['previous_hash'] =  str(transaction.objects.all().last().blockhash)    #3
    data['amount'] = str(amount)                                                #4
    data['timestamp'] =  str(first_timestamp)                                   #5
    data["nonce"] = str(nonce)
    data = collections.OrderedDict(sorted(data.items()))
    datashash  = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()
    return datashash



def checktimepass():
    lasttime = arrow.utcnow().to("GMT")
    gethours = int(lasttime.format('H'))
    getminute = int(lasttime.format('m'))
    print('hours %s and minutes %s' % (gethours, getminute))
    if gethours == 00:
        if getminute <= 15:
            return True
        else:
            return False
    elif gethours == 4:
        if getminute <= 15:
            return True
        else:
            return False
    elif gethours == 8:
        if getminute <= 15:
            return True
        else:
            return False
    elif gethours == 12:
        if getminute <= 15:
            return True
        else:
            return False
    elif gethours == 16:
        if getminute <= 15:
            return True
        else:
            return False
    elif gethours == 20:
        if getminute <= 15:
            return True
        else:
            return False

    elif gethours == 14:
        if getminute <= 15:
            return True
        else:
            return False
    else:
        return False



print(checktimepass())
