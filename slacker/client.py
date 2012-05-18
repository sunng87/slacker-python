import random
import itertools
import struct

import gevent
import gevent.socket
import gevent.event

from protocol import *
import cStringIO as StringIO

class Connection(object):
    def __init__(self, addr):
        self.addr = (addr.split(":")[0], int(addr.split(":")[1]))
        self.sock = None
        self.connect_lock = gevent.event.Event()
        self.transid = itertools.count()
        self.reqs = {}

    def connect(self):
        while True:
            try:
                self.sock = gevent.socket.create_connection(self.addr)
                self.connect_lock.set()
                self.eloop = gevent.spawn(self.readLoop)
                break
            except:
                gevent.sleep(5)

    def reconnect(self):
        self.close()
        self.connect()


    def readLoop(self):
        while True:
            try:
                _, tid, packetType = readHeader(self.sock)
                resp = None
                if packetType == PROTOCOL_PACKET_TYPE_RESPONSE:
                    resp = readResponse(self.sock)
                    
                elif packetType == PROTOCOL_PACKET_TYPE_ERROR:
                    resp = readError(self.sock)
                    
                cb = self.reqs[tid]
                cb.set(resp)
                del self.reqs[tid]
            except struct.error:
                self.reconnect()
                break
            except IOError:
                self.reconnect()
                break

    def send(self, request):
        transid = self.transid.next()
        cb = gevent.event.AsyncResult()
        self.reqs[transid] = cb

        buf = StringIO.StringIO()
        writeHeader(buf, transid, PROTOCOL_PACKET_TYPE_REQUEST)
        writeRequest(buf, request)
        data = buf.getvalue()
        buf.close()
        
        try:
            self.connect_lock.wait()
            self.sock.send(data)
        except:
            ## reconnect
            self.reconnect()

        return cb

    def close(self):
        if self.eloop:
            gevent.kill(self.eloop)
        if self.sock:
            self.sock.close()
        self.reqs.clear()
        self.connect_lock.clear()

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
        try:
            result = cb.get(timeout=10)
        except Timeout, t:
            raise RuntimeError("Timeout")
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

