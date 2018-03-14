#-*- coding: utf-8 -*-
import sys, json, requests, django ,os ,base64, collections,hashlib, math
from django.utils.encoding import smart_str
from ecdsa import SigningKey, SECP256k1, NIST384p, BadSignatureError, VerifyingKey
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
import netifaces as ni
from cloudbank.wsgi import application as wsgi_handler
django.setup()
from core.models import transaction
from cloudbank.utils import instantwallet, generate_wallet_from_pkey, generate_pubkey_from_prikey, checkreward

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
connectWS

ni.ifaddresses('eth0')
ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']



class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print(type(payload))
            print(payload)
            payload = payload.decode('utf-8')
            myjson = json.loads(payload)
            if myjson["server"]:
                print("that message came from server")
                addnewnode(myjson["host"])
            else:
                print(myjson["message"])
                myjson["host"] = ip
                myjson = json.dumps(myjson)
                self.factory.broadcast(myjson)
        else:
            print(payload)
            print(json.loads(payload))
            myjson = json.loads(payload)
            if myjson["server"]:
                print("that message came from server")
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
    #self.broadcast serverda yayn yapar..

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
            msg = "ok"
            c.sendMessage(msg)
            print("messaj disaridan aldim {}".format(c.peer))



class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("33 'den servera connected': {0}".format(response.peer))

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
        print("onmessage")
        allify = {}
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:

            payloaded = json.loads(payload.decode('utf-8'))
            print(payloaded["host"])
            if str(payloaded["host"]) == str(ip):
                print("bu zaten sensin")
            else:

                payloaded = json.loads(payload.decode('utf-8'))
                if 'sender' in payloaded:

                    data['sender'] = str(payloaded["sender"])                                       #1
                    data['receiver'] = str(payloaded["receiver"])                                   #2
                    data['previous_hash'] = str(transaction.objects.all().last().blockhash)         #3
                    data['amount'] = str(payloaded["amount"])                                       #4
                    data['timestamp'] = str(payloaded["timestamp"])                                 #5
                    data["nonce"] = str(payloaded["nonce"])
                    data = collections.OrderedDict(sorted(data.items()))
                    datashash  = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()
                    sig = json.loads(payloaded["P2PKH"])

                    print("datahashhere", datashash.encode('utf-8'))
                    print("sigbyte is here", sig)
                    print("sende weas here", payloaded["sender"])
                    wllt = generate_wallet_from_pkey(payloaded["sender"])
                    print(checkreward())
                    try:
                        sigbyte =  bytes.fromhex(sig)
                        vk = VerifyingKey.from_string(bytes.fromhex(payloaded["sender"]), curve=SECP256k1)
                        tt = vk.verify(sigbyte, datashash.encode('utf-8')) # True
                    except BadSignatureError:
                        print("unbelieveable")
                        data["response"] = "unbelieveable"
                        newtrans = transaction(sender=payloaded["sender"],
                        senderwallet=wllt,
                        receiver=payloaded["receiver"],
                        prevblockhash=transaction.objects.all().last().blockhash,
                        blockhash=payloaded["blockhash"],
                        amount=payloaded["amount"],
                        nonce=payloaded["nonce"],
                        first_timestamp=payloaded["timestamp"],
                        P2PKH=payloaded["P2PKH"],
                        verification=False
                        ).save()
                        print("badsignature")

                    newtrans = transaction(sender=payloaded["sender"],
                    senderwallet=wllt,
                    receiver=payloaded["receiver"],
                    prevblockhash=transaction.objects.all().last().blockhash,
                    blockhash=payloaded["blockhash"],
                    amount=payloaded["amount"],
                    nonce=payloaded["nonce"],
                    first_timestamp=payloaded["timestamp"],
                    P2PKH=payloaded["P2PKH"],
                    verification=True
                    ).save()

                else:
                    print("other message")
                BroadcastServerFactory.broadcast(payload)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        def byebye():
            self.sendMessage(u"Good byee, from 138.68.94.33  !".encode('utf8'))

        byebye()


def syncfirst():
    r = requests.get('http://159.89.197.53/api/v1/alltransactions/')
    alltrans = r.json()
    for x in alltrans["alltestsarecomplated"]:
        try:
            mytransactions = transaction.objects.get(blockhash=x["blockhash"])
        except transaction.DoesNotExist:
            newtrans = transaction(sender=x["sender"],
                senderwallet=x["senderwallet"],
                receiver=x["receiver"],
                prevblockhash=x["prevblockhash"],
                blockhash=x["blockhash"],
                amount=x["amount"],
                nonce=x["nonce"],
                first_timestamp=x["first_timestamp"],
                P2PKH=x["P2PKH"],
                verification=x["verification"])
            newtrans.save()
    print("everyting is up-da-te")







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
