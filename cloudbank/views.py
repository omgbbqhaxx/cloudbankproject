#-*- coding: utf-8 -*-
import uuid , json , string , random, urllib, base64, os, sys, time, pickle, collections, math
from django.utils.encoding import smart_str
from ecdsa import SigningKey, SECP256k1, NIST384p, BadSignatureError, VerifyingKey
from django.http import *
from django import template
from django.shortcuts import *
from django.http import HttpResponse
from django.contrib.auth import logout
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from cloudbank.utils import instantwallet, generate_wallet_from_pkey, generate_pubkey_from_prikey
from django.db.models import Avg, Sum, Count
import base64, bson, websocket, hashlib
from core.models import transaction
from django.template.defaultfilters import stringfilter
import netifaces as ni
ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']


def landing(request):
    try:
        pubkey = request.session['pubkey']
        prikey = request.session['prikey']
        print(pubkey)
        print(pubkey.encode('utf-8'))
        print(type(pubkey.encode('utf-8')))
        wallet_id =  generate_wallet_from_pkey(pubkey) #hashlib.sha256(pubkey.encode('utf-8')).hexdigest() #SHA256.new(pubkey).hexdigest()
        balance = getbalance(pubkey)
        if balance is None:
            balance = 0
        return render(request, "ok.html", locals())
    except KeyError:
        return render(request, "index.html", locals())


def ws(request):
    ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    transactions = transaction.objects.all()[::-1][0:8]
    return render(request, "ws.html", locals())

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


def getbalance(pubkey):
    wallet_id =  generate_wallet_from_pkey(pubkey)
    outgoing = transaction.objects.filter(sender=pubkey).aggregate(Sum('amount'))['amount__sum']
    income = transaction.objects.filter(receiver=wallet_id).aggregate(Sum('amount'))['amount__sum']
    # print(outgoing)
    # print(income)

    if income and outgoing:
        # print("user have both")
        return(income - outgoing)
    elif outgoing is None:
        # print("user dont have  outgoing")
        return income
    elif income is None:
        return 0
    else:
        return 0

def login(request):
    try:
        pubkey = request.session['pubkey']
        prikey = request.session['prikey']
        return HttpResponseRedirect('/')
    except KeyError:
        return render(request, "login.html", locals())

def logout(request):
    request.session.clear()
    return HttpResponseRedirect('/')


def createnewwallet(request):
    data = {}
    datas = {}
    qey = instantwallet()
    data['private_key'] = qey[0]
    data['wallet_id'] = qey[1]
    data['pkey'] = qey[2]
    datas['wallet'] = data
    return HttpResponse(json.dumps(datas), content_type = "application/json")



@csrf_exempt
def checkwallet(request):
    data = {}
    prikey = request.POST.get('prikey').strip()
    message = b"hello"
    try:
        sk = SigningKey.from_string(bytes.fromhex(prikey), curve=SECP256k1)
        vk = sk.get_verifying_key() #public_key
        print(vk.to_string().hex())
    except UnicodeDecodeError:
        data["response"] = "Check your wallet details"
        return HttpResponse(json.dumps(data), content_type="application/json")
    except TypeError:
        data["response"] = "Check your wallet details"
        return HttpResponse(json.dumps(data), content_type = "application/json")
    except ValueError:
        data["response"] = "Check your wallet details ValueError"
        return HttpResponse(json.dumps(data), content_type = "application/json")

    try:
        sig = sk.sign(message)
        test = vk.verify(sig, b"hello") # True
    except BadSignatureError:
        data["response"] = "access_denied"
        return HttpResponse(json.dumps(data), content_type = "application/json")
    request.session['pubkey'] = vk.to_string().hex()
    request.session['prikey'] = prikey
    data["response"] = "access_approved"
    return HttpResponse(json.dumps(data), content_type = "application/json")



def miner(first_timestamp, senderwalletid, receiverhex,amount):
    data = {}
    for nonce in range(0,10000000):
        data['senderpublickey'] = str(senderwalletid) #1
        data['receiverhex'] = str(receiverhex)      #2
        data['previous_hash'] =  str(transaction.objects.all().last().blockhash) #3
        data['amount'] = str(amount) #4
        data['timestamp'] =  str(first_timestamp) #5
        data["nonce"] = str(nonce)
        data = collections.OrderedDict(sorted(data.items()))
        datashash  = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()
        last2char = datashash[-2:]
        if last2char == "01":
            return(nonce)
        else:
            # print(nonce)
            continue


@csrf_exempt
def sendcloudcoin(request):
    allify = {}
    data = {}
    if request.method == 'POST':
        senderprivatekey = request.POST.get('sprikey')
        receiverwallet = request.POST.get('receiverwallet').strip()
        amount = request.POST.get('amount').strip()
        sender = generate_pubkey_from_prikey(senderprivatekey)

        if not receiverwallet:
            allify['response'] = "fail"
            allify['explain'] = "Please fill the receiver box"
            return HttpResponse(json.dumps(allify), content_type = "application/json")
        try:
            amount = int(request.POST.get('amount').strip())
        except ValueError:
            allify['response'] = "fail"
            allify['explain'] = "Please fill the balance box"
            return HttpResponse(json.dumps(allify), content_type = "application/json")
        if int(amount) <= 0:
            allify['response'] = "fail"
            allify['explain'] = "insufficient balance"
            return HttpResponse(json.dumps(allify), content_type = "application/json")
        balance = getbalance(sender)
        if balance is None:
            balance = 0
        if int(amount) > int(balance):
            allify['response'] = "fail"
            allify['explain'] = "insufficient balance"
            return HttpResponse(json.dumps(allify), content_type = "application/json")
        else:
            first_timestamp = time.time()
            data['senderpublickey'] = str(sender) #1
            data['receiverhex'] = str(receiverwallet)      #2
            data['previous_hash'] = str(transaction.objects.all().last().blockhash) #3
            data['amount'] = str(amount) #4
            data['timestamp'] = str(first_timestamp) #5
            perfect =  miner(first_timestamp, sender, receiverwallet, amount)
            data["nonce"] = str(perfect)
            data = collections.OrderedDict(sorted(data.items()))
            datashash  = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()

            try:
                sk = SigningKey.from_string(bytes.fromhex(senderprivatekey), curve=SECP256k1)
                vk = sk.get_verifying_key() #public_key
                print(vk.to_string().hex())
            except UnicodeDecodeError:
                data["response"] = "Check your wallet details"
                return HttpResponse(json.dumps(data), content_type="application/json")
            digitalSignature = sk.sign(datashash.encode('utf-8'))
            digitalSignature = json.dumps(digitalSignature.hex())

            newtrans = transaction(sender=sender,
            receiver=receiverwallet,
            prevblockhash=transaction.objects.all().last().blockhash,
            blockhash=datashash,
            amount=amount,
            nonce=perfect,
            first_timestamp=first_timestamp,
            P2PKH=digitalSignature,
            verification=True
            )
            newtrans.save()
            ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
            geturl = "http://{}/gettransaction/{}/".format(ip,newtrans.id)
            test = {"server":False,
            "sender":sender,
            "receiver":receiverwallet,
            "prevblockhash":transaction.objects.all().last().blockhash,
            "blockhash":datashash,
            "amount":amount,
            "nonce":perfect,
            "first_timestamp":first_timestamp,
            "P2PKH":digitalSignature,
            "verification":True,
            "block" : transaction.objects.all().last().id + 1,
            "message":"new_transaction",
            "url":geturl}

            payload = json.dumps(test)

            ws = websocket.WebSocket()
            wsip = "ws://{}:9000".format(ip)
            ws.connect(wsip)
            ws.send(payload)

            allify['response'] = "ok"
            allify['datashash'] = datashash
            allify['datastring'] = json.dumps(allify)
            return HttpResponse(json.dumps(allify), content_type = "application/json")
