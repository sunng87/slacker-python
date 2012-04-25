import random
import itertools

import gevent
import gevent.socket
import gevent.event

from protocol import *
import cStringIO as StringIO

class Connection(object):
    def __init__(self, addr):
        self.host = addr.split(":")[0]
        self.port = int(addr.split(":")[1])
        self.sock = None
        self.transid = itertools.count()
        self.reqs = {}

    def connect(self):
        self.sock = gevent.socket.create_connection((self.host, self.port))
        self.clientLoop = gevent.spawn(self.readLoop)

    def readLoop(self):
        while True:
            _, tid, packetType = readHeader(self.sock)
            resp = None
            if packetType == PROTOCOL_PACKET_TYPE_RESPONSE:
                resp = readResponse(self.sock)

            elif packetType == PROTOCOL_PACKET_TYPE_ERROR:
                resp = readError(self.sock)
            cb = self.reqs[tid]
            cb.set(resp)
            del self.reqs[tid]

    def send(self, request):
        transid = self.transid.next()
        cb = gevent.event.AsyncResult()
        self.reqs[transid] = cb

        buf = StringIO.StringIO()
        writeHeader(buf, transid, PROTOCOL_PACKET_TYPE_REQUEST)
        writeRequest(buf, request)
        data = buf.getvalue()
        buf.close()

        self.sock.send(data)

        return cb

    def close(self):
        self.clientLoop.kill()
        self.sock.close()
        self.reqs.clear()

class Client(object):
    def __init__(self, addrs):
        self.connections = map(lambda m: Connection(m), addrs)
        for c in self.connections:
            c.connect()

    def call(self, fname, args):
        req = SlackerRequest(PROTOCOL_CONTENT_TYPE_CLJ, fname, args)
        req.serialize()
        conn = random.choice(self.connections)
        cb = conn.send(req)
        result = cb.get()
        if isinstance(result, SlackerResponse):
            if result.code == PROTOCOL_RESULT_CODE_SUCCESS:
                result.desrialize()
                return result.body
            else:
                raise RuntimeError("Error code: "+ str(result.code))
        else:
            code = result.code
            raise RuntimeError("Error code: " + str(code))

class Proxy(object):
    def __init__(self, client, namespace):
        self.client = client
        self.namespace = namespace

    def __getattr__(self, name):
        return (lambda *x: self._invoke(name, x))

    def _invoke(self, name, args):
        return self.client.call(self.namespace+"/"+name, args)

