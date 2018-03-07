#-*- coding: utf-8 -*-
import sys, bson, json, pickle

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
import netifaces as ni

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
connectWS
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
            print("selam ", payload)
            print("selam ", payload.decode('utf-8'))
            payload = json.loads(payload.decode('utf-8'))

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
            print("broadcast", msg)
            #msg = json.dumps(msg)
            print("i get a message from outside {}".format(c.peer))
            c.sendMessage(msg.encode('utf8'))


class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            payloaded = json.loads(payload.decode('utf-8'))
            print(payloaded["host"])
            if str(payloaded["host"]) == str(ip):
                print("bu zaten sensin")
            else:
                payload = json.dumps(payload)
                BroadcastServerFactory.broadcast(payload)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))




if __name__ == '__main__':
    print("here works one times..")
    ServerFactory = BroadcastServerFactory
    factory = ServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = BroadcastServerProtocol
    reactor.listenTCP(9000, factory)
    reactor.run()
