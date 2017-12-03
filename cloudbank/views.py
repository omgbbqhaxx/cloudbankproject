#-*- coding: utf-8 -*-
import uuid , json , string , random, urllib, base64, os, sys, time, pickle, collections
from django.utils.encoding import smart_str
from django.http import *
from django import template
from django.shortcuts import *
from django.http import HttpResponse
from django.contrib.auth import logout
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from cloudbank.myrsa import *
from django.db.models import Avg, Sum, Count
import base64, bson, websocket, hashlib
from core.models import transaction
from django.template.defaultfilters import stringfilter
import netifaces as ni

ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']


def landing(request):
    try:
        pubkey = request.session['pubkey'].encode('utf-8')
        prikey = request.session['prikey'].encode('utf-8')
        wallet_id = SHA256.new(pubkey).hexdigest()
        balance = getbalance(wallet_id)
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
                     "senderhexdigest": trr.senderhexdigest,
                     "receiver": trr.receiver,
                     "receiverhexdigest": trr.receiverhexdigest,
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
                     "senderhexdigest": trr.senderhexdigest,
                     "receiver": trr.receiver,
                     "receiverhexdigest": trr.receiverhexdigest,
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


def getbalance(wallet_id):
    outgoing = transaction.objects.filter(senderhexdigest=wallet_id).aggregate(Sum('amount'))['amount__sum']
    income = transaction.objects.filter(receiverhexdigest=wallet_id).aggregate(Sum('amount'))['amount__sum']
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
    data['private_key'] = base64.b64encode(qey[0]).decode('utf-8')
    data['public_key'] = base64.b64encode(qey[1]).decode('utf-8')
    data['wallet_id'] = qey[2]
    datas['wallet'] = data
    return HttpResponse(json.dumps(datas), content_type = "application/json")



@csrf_exempt
def checkwallet(request):
    data = {}
    if request.method == 'POST':
        pubkey = request.POST.get('pubkey').strip()
        prikey = request.POST.get('prikey').strip()
        # print(pubkey)
        try:
            key = RSA.importKey(base64.b64decode(pubkey))
            public_key = key.publickey()
            enc_data = public_key.encrypt('cloudbank'.encode('utf-8'), 32)
            pass_hex = base64.b64encode(enc_data[0])
            enc_data = base64.b64decode(pass_hex)
            newkey =  RSA.importKey(base64.b64decode(prikey))
            x = newkey.decrypt(enc_data)
        except UnicodeDecodeError:
            data["response"] = "Check your wallet details UnicodeDecodeError"
            return HttpResponse(json.dumps(data), content_type = "application/json")
        except TypeError:
            data["response"] = "Check your wallet details"
            return HttpResponse(json.dumps(data), content_type = "application/json")
        except ValueError:
            data["response"] = "Check your wallet details ValueError"
            return HttpResponse(json.dumps(data), content_type = "application/json")
        if x == "cloudbank".encode('utf-8'):
            request.session['pubkey'] = base64.b64decode(pubkey).decode('utf-8')
            request.session['prikey'] = base64.b64decode(prikey).decode('utf-8')
            data["response"] = "access_approved"
            return HttpResponse(json.dumps(data), content_type = "application/json")
        else:
            data["response"] = "access_denied"
            return HttpResponse(json.dumps(data), content_type = "application/json")
    else:
        data["response"] = "ONLY POST"
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
        senderpubkey = request.POST.get('spubkey')
        senderprivatekey = request.POST.get('sprikey')
        senderwalletid = request.POST.get('swid')
        receiver = request.POST.get('pubkey').strip()
        receiverhex  = SHA256.new(base64.b64decode(receiver)).hexdigest()
        amount = request.POST.get('amount').strip()

        if int(amount) <= 0:
            allify['response'] = "fail"
            return HttpResponse(json.dumps(allify), content_type = "application/json")

        balance = getbalance(senderwalletid)
        if balance is None:
            balance = 0
        if int(amount) > int(balance):
            allify['response'] = "fail"
            return HttpResponse(json.dumps(allify), content_type = "application/json")
        else:
            first_timestamp = time.time()
            data['senderpublickey'] = str(senderwalletid) #1
            data['receiverhex'] = str(receiverhex)      #2
            data['previous_hash'] = str(transaction.objects.all().last().blockhash) #3
            data['amount'] = str(amount) #4
            data['timestamp'] = str(first_timestamp) #5
            perfect =  miner(first_timestamp, senderwalletid, receiverhex, amount)
            data["nonce"] = str(perfect)
            data = collections.OrderedDict(sorted(data.items()))


            datashash  = SHA256.new(json.dumps(data).encode('utf-8')).hexdigest()
            # print(datashash)
            # print(datashash.encode('utf-8'))
            rsakey = RSA.importKey(senderpubkey)
            rsakey = RSA.importKey(senderprivatekey)
            digitalSignature = rsakey.sign(datashash.encode('utf-8'),'')
            digitalSignature = json.dumps(digitalSignature)

            newtrans = transaction(sender=base64.b64encode(senderpubkey.encode('utf-8')),
            senderhexdigest=senderwalletid,
            receiver=receiver,
            receiverhexdigest=receiverhex,
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

            # print("okasodkaod", newtrans.id)
            geturl = "http://{}/gettransaction/{}/".format(ip,newtrans.id)

            # print("gettypeprepe", type(receiverhex))
            test = {"server":False,
            "sender":base64.b64encode(senderpubkey.encode('utf-8')).decode('utf-8'),
            "senderhexdigest":senderwalletid,
            "receiver":receiver,
            "receiverhexdigest":receiverhex,
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
