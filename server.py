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


def addnewnode(host):
    ws = "ws://{}:9000".format(host)
    #factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
    factory = WebSocketClientFactory(ws)
    factory.protocol = MyClientProtocol
    reactor.connectTCP(host, 9000, factory)



class BroadcastServerProtocol(WebSocketServerProtocol):
    #websocketten gelen mesajlar buraya düşer..
    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
            print("is it binary", isBinary)
            print("check payload type from here  x)", type(payload))
            print("check payload from here  x)", payload)

            if isBinary:
                #sorun olduğunda buraya gelecek demektir.
                print("selam ", payload )
                payload = json.loads(payload)
                if payload["server"]:
                    print("bu mesaj serverdan gelmis demek")
                    addnewnode(payload["host"])
                else:
                    print(payload["message"])
                    payload["host"] = ip
                    payload = json.dumps(payload) #tekrar şifreleyip server ile paykaş
                    self.factory.broadcast(payload)
            else:
                #Binary olsada buraya geliyor.
                print("else : selam ", payload)
                print("else testfigfsa ", type(payload))
                payload = json.loads(payload.decode('utf8'))
                if payload["server"]:
                    print("bu mesaj serverdan gelmis demek")
                    addnewnode(payload["host"])
                else:
                    print(payload["message"])
                    payload["host"] = ip
                    payload = json.dumps(payload) #tekrar şifreleyip server ile paykaş
                    self.factory.broadcast(payload)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

clients = []

class BroadcastServerFactory(WebSocketServerFactory):
    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
    def register(self, client):
        if client not in clients:
            print("registered client {}".format(client.peer))
            print(clients)
            tcp, host, port = client.peer.split(":")
            print(host)
            clients.append(client)

    def unregister(self, client):
        if client in clients:
            print("unregistered client {}".format(client.peer))
            clients.remove(client)

    @classmethod
    def broadcast(self, msg):
        for c in clients:
            print("im at broadcast",msg)
            print("im at broadcast type msg", type(msg))
            print("messaj disaridan aldim {}".format(c.peer))
            if isinstance(msg, dict):
                print("class is dict")
                msg = json.dumps(msg)
                c.sendMessage(msg)
            else:
                c.sendMessage(msg.encode('utf-8')) #.encode('utf8') str object no decode






class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

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
                    #print(checkreward())
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
                BroadcastServerFactory.broadcast(payloaded)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))




if __name__ == '__main__':
    print("start")
    ServerFactory = BroadcastServerFactory
    factory = ServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = BroadcastServerProtocol
    reactor.listenTCP(9000, factory)
    reactor.run()
