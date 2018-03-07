###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import sys, json, requests, django ,os ,base64, collections

from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
import netifaces as ni
from cloudbank.wsgi import application as wsgi_handler
django.setup()

from core.models import transaction

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
connectWS


BLIST = [u"ws://159.89.197.53:9000"]
#BLIST = [u"ws://128.199.247.189:9000",u"ws://127.0.0.1:9000"]
BLISTTWO =  ["159.89.197.53"]
#BLISTTWO =  ["128.199.247.189","127.0.0.1"]

ni.ifaddresses('eth0')
ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']



class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("isBinary olmak zorunda")
        else:
            print(payload)
            print(json.loads(payload))
            myjson = json.loads(payload)
            if myjson["server"]:
                print("bu mesaj serverdan gelmiş demektir")
                addnewnode(myjson["host"])
            else:
                print(myjson["message"])
                myjson["host"] = ip
                myjson = json.dumps(myjson)
                self.factory.broadcast(myjson)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

clients = []

class BroadcastServerFactory(WebSocketServerFactory):
    #self.broadcast serverda yayın yapar..

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)


    def register(self, client):
        if client not in clients:
            print("registered client {}".format(client.peer))
            clients.append(client)

    def unregister(self, client):
        if client in clients:
            print("unregistered client {}".format(client.peer))
            clients.remove(client)


    @classmethod
    def broadcast(self, msg):
        for c in clients:
            c.sendMessage(msg)
            print("messaj disaridan aldım {}".format(c.peer))



class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("33 'den servera baglanıldı': {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        #kullanıcı servera ilk bağlandığı zaman bu mesaj gönderilir.
        def hello():
            #self.sendMessage(u"Hello, from 138.68.94.33  !".encode('utf8'))
            data = {}
            data["server"] = True
            data["host"] = ip
            mybinarydata = json.dumps(data)
            self.sendMessage(mybinarydata.encode('utf8'))
        hello()

    def onMessage(self, payload, isBinary):
        data = {}
        allify = {}
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("burası mı çalışıyor 11082")
            payloaded = json.loads(payload.decode('utf-8'))
            print(payloaded["host"])
            if str(payloaded["host"]) == str(ip):
                print("bu zaten sensin")
            else:
                payloaded = json.loads(payload.decode('utf-8'))
                if 'senderhexdigest' in payloaded:
                    print(payload)
                    data['senderpublickey'] = str(payloaded["senderhexdigest"])  #1
                    data['receiverhex'] = str(payloaded["receiverhexdigest"])       #2
                    data['previous_hash'] = str(transaction.objects.all().last().blockhash) #3
                    data['amount'] = str(payloaded["amount"]) #4
                    data['timestamp'] = str(payloaded["first_timestamp"]) #5
                    data["nonce"] = str(payloaded["nonce"])
                    data = collections.OrderedDict(sorted(data.items()))
                    print("ozel data",data)
                    datashash  = SHA256.new(json.dumps(data).encode('utf-8')).hexdigest()
                    print(datashash)
                    datashash = datashash.encode('utf-8')
                    newkey = RSA.importKey(base64.b64decode(payloaded["sender"]))
                    if(newkey.verify(datashash, json.loads(payloaded["P2PKH"]) )):
                        print("Match")
                    else:
                        print("failift")

                    newtrans = transaction(sender=payloaded["sender"],
                    receiver=payloaded["receiver"],
                    prevblockhash=transaction.objects.all().last().blockhash,
                    blockhash=payloaded["blockhash"],
                    amount=payloaded["amount"],
                    nonce=payloaded["nonce"],
                    first_timestamp=payloaded["first_timestamp"],
                    P2PKH=payloaded["P2PKH"],
                    verification=True
                    ).save()

                else:
                    print("başka bir mesajjj")
                BroadcastServerFactory.broadcast(payload)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        def byebye():
            self.sendMessage(u"Good byee, from 138.68.94.33  !".encode('utf8'))

        byebye()


def syncfirst():
    r = requests.get('http://159.89.197.53/alltransactions/')
    alltrans = r.json()
    print(type(alltrans))
    lasttransactionid = alltrans["alltestsarecomplated"][-1]["id"]
    try:
        gtfd = transaction.objects.all().reverse()[0] #[::-1]
    except IndexError:
        for x in alltrans["alltestsarecomplated"]:
            print(x["id"])
            newtrans = transaction(sender=x["sender"],
            receiver=x["receiver"],
            prevblockhash=x["prevblockhash"],
            blockhash=x["blockhash"],
            amount=x["amount"],
            nonce=x["nonce"],
            first_timestamp=x["first_timestamp"],
            P2PKH=x["P2PKH"],
            verification=x["verification"])
            newtrans.save()

    gtfd = transaction.objects.all()[::-1][0]

    if(int(lasttransactionid) > int(gtfd.id)):
        for x in alltrans["alltestsarecomplated"]:
            if(int(x["id"]) > int(gtfd.id)):
                print(x["id"])
                newtrans = transaction(sender=x["sender"],
                receiver=x["receiver"],
                prevblockhash=x["prevblockhash"],
                blockhash=x["blockhash"],
                amount=x["amount"],
                nonce=x["nonce"],
                first_timestamp=x["first_timestamp"],
                P2PKH=x["P2PKH"],
                verification=x["verification"])
                newtrans.save()
    else:
        print("already synced")






if __name__ == '__main__':

    #log.startLogging(sys.stdout)
    syncfirst()


    ServerFactory = BroadcastServerFactory

    factory = ServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = BroadcastServerProtocol
    reactor.listenTCP(9000, factory)

    factory = WebSocketClientFactory(u"ws://159.89.197.53:9000")
    factory.protocol = MyClientProtocol

    reactor.connectTCP(u"159.89.197.53", 9000, factory)

    reactor.run()
