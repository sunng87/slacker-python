import random
import itertools
import struct
import cStringIO as StringIO
import time
import socket
import threading

from protocol import *

class Connection(object):
    def __init__(self, addr):
        self.addr = (addr.split(":")[0], int(addr.split(":")[1]))
        self.sock = None
        self.connect_lock = threading.Event()
        self.transid = itertools.count()

    def connect(self):
        while True:
            try:
                self.sock = socket.create_connection(self.addr)
                self.connect_lock.set()
                break
            except:
                time.sleep(5)

    def reconnect(self):
        self.close()
        self.connect()

    def send(self, request):
        transid = self.transid.next()

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

    def receive(self):
        try:
            _, tid, packetType = readHeader(self.sock)
            resp = None
            if packetType == PROTOCOL_PACKET_TYPE_RESPONSE:
                resp = readResponse(self.sock)

            elif packetType == PROTOCOL_PACKET_TYPE_ERROR:
                resp = readError(self.sock)

            return resp

        except struct.error:
            self.reconnect()

        except IOError:
            self.reconnect()

    def close(self):
        if self.sock:
            self.sock.close()

        self.connect_lock.clear()

class Client(object):
    def __init__(self, addrs, timeout=10):
        self.connections = map(lambda m: Connection(m), addrs)
        self.timeout = timeout
        for c in self.connections:
            c.connect()

    def call(self, fname, args):
        req = SlackerRequest(PROTOCOL_CONTENT_TYPE_CLJ, fname, args)
        req.serialize()
        conn = random.choice(self.connections)
        conn.send(req)
        result = conn.receive()

        if isinstance(result, SlackerResponse):
            if result.code == PROTOCOL_RESULT_CODE_SUCCESS:
                result.desrialize()
                return result.body
            else:
                raise RuntimeError("Error code: "+ str(result.code))
        else:
            code = result.code
            raise RuntimeError("Error code: " + str(code))

    def close(self):
        for c in self.connections:
            c.close()
