import random
import itertools
import struct

import gevent
from gevent import socket
from gevent import event

from protocol import *
import cStringIO as StringIO

class Connection(object):
    def __init__(self, addr):
        self.addr = (addr.split(":")[0], int(addr.split(":")[1]))
        self.sock = None
        self.eloop = None
        self.started = False
        self.connect_lock = event.Event()
        self.transid = itertools.count()
        self.reqs = {}

    def connect(self):
        self.started = True
        self.sock = socket.create_connection(self.addr)
        self.connect_lock.set()
        self.eloop = gevent.spawn(self.readLoop)

    def _reconnect(self):
        self.close()
        while True:
            try:
                self.connect()
                break
            except:
                gevent.sleep(5)

    def readLoop(self):
        while self.started:
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
                self._reconnect()
                break
            except IOError:
                self._reconnect()
                break

    def send(self, request, timeout):
        transid = self.transid.next()
        cb = event.AsyncResult()
        self.reqs[transid] = cb

        buf = StringIO.StringIO()
        writeHeader(buf, transid, PROTOCOL_PACKET_TYPE_REQUEST)
        writeRequest(buf, request)
        data = buf.getvalue()
        buf.close()

        try:
            if self.sock is None:
                self.connect()

            self.connect_lock.wait(timeout=timeout)
            self.sock.send(data)
        except gevent.Timeout:
            raise RuntimeError("Timeout")
            ## reconnect
            gevent.spawn(self._reconnect)
        except:
            ## reconnect
            gevent.spawn(self._reconnect)

        return cb

    def close(self):
        self.started = False
        if self.eloop:
            gevent.kill(self.eloop)
        if self.sock:
            self.sock.close()
        self.reqs.clear()
        self.connect_lock.clear()

class Client(object):
    def __init__(self, addr, timeout=10, content_type=PROTOCOL_CONTENT_TYPE_CLJ):
        self.timeout = timeout
        conn = Connection(addr)
        #conn.connect()
        self.conn = conn
        self.started = True
        self.content_type = content_type

    def call(self, fname, args):
        if not self.started:
            raise RuntimeError("Client closed.")

        req = SlackerRequest(self.content_type, fname, args)
        req.serialize()
        cb = self.conn.send(req, self.timeout)
        try:
            result = cb.get(timeout=self.timeout)
        except gevent.Timeout:
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

    def close(self):
        self.conn.close()
        self.started = False
