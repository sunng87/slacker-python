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
        self.transid = 0
        self.reqs = {}

    def connect(self):
        self.sock = gevent.socket.create_connection(self.host, self.port)
        self.clientLoop = gevent.spawn(self.readLoop)

    def readLoop(self):
        while True:
            _, tid, packetType = readHeader(self.sock)
            resp = None
            if packetType == PROTOCOL_PACKET_TYPE_RESPONSE:
                resp = readResponse(self.sock)
                resp.desrialize()
            elif packetType == PROTOCOL_PACKET_TYPE_ERROR:
                resp = readError(self.sock)
            cb = self.reqs[tid]
            cb.set(resp)
            del self.reqs[tid]

    def send(self, request):
        self.request.serialize()
        transid = self.transid
        cb = gevent.event.AsyncResult()
        self.reqs[transid] = cb

        self.transid += 1

        buf = StringIO.StringIO()
        writeHeader(buf, transid, PROTOCOL_PACKET_TYPE_REQUEST)
        writeRequest(buf, request)
        self.sock.send(buf.getvalue())

        return cb


    
