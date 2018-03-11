#-*- coding: utf-8 -*-
import uuid , json , string , random, urllib, base64, os, sys, time, pickle, collections, math, arrow
from django.utils.encoding import smart_str
from ecdsa import SigningKey, SECP256k1, NIST384p, BadSignatureError, VerifyingKey
from django.http import *
from django import template
from django.shortcuts import *
from django.http import HttpResponse
from django.contrib.auth import logout
import hashlib
from django.conf import settings
from core.models import transaction
from cloudbank.utils import instantwallet, generate_wallet_from_pkey, generate_pubkey_from_prikey


def getwalletfrompkey(request, pkey):
    data = {}
    wallet = generate_pubkey_from_prikey(pkey)
    data["public_key"] = pkey
    data["wallet"] = wallet
    return HttpResponse(json.dumps(data), content_type = "application/json")



def gettransaction(request, tid):
        data = {}
        trr = transaction.objects.get(id=int(tid))
        data = {"sender" : trr.sender,
                     "receiver": trr.receiver,
                     "prevblockhash": trr.prevblockhash,
                     "blockhash": trr.blockhash,
                     "amount": trr.amount,
                     "nonce": trr.nonce,
                     "first_timestamp": trr.first_timestamp,
                     "saved_timestamp": trr.saved_timestamp.strftime("%Y-%m-%d"),
                     "P2PKH": trr.P2PKH,
                     "verification": trr.verification}
        return HttpResponse(json.dumps(data), content_type = "application/json")





def alltransactions(request):
    data = {}
    txs = []
    transactions = transaction.objects.all()
    for trr in transactions:
        gettrs = {"sender" : trr.sender,
                     "receiver": trr.receiver,
                     "prevblockhash": trr.prevblockhash,
                     "blockhash": trr.blockhash,
                     "amount": trr.amount,
                     "nonce": trr.nonce,
                     "first_timestamp": trr.first_timestamp,
                     "saved_timestamp": trr.saved_timestamp.strftime("%Y-%m-%d"),
                     "P2PKH": trr.P2PKH,
                     "verification": trr.verification,
                     "id":trr.id}
        txs.append(gettrs)

    data['alltestsarecomplated'] = txs
    return HttpResponse(json.dumps(data), content_type = "application/json")
