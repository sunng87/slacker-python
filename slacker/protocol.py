import struct
import json
import clj

PROTOCOL_VERSION = 5

PROTOCOL_PACKET_TYPE_REQUEST = 0
PROTOCOL_PACKET_TYPE_RESPONSE = 1
PROTOCOL_PACKET_TYPE_ERROR = 4

PROTOCOL_CONTENT_TYPE_JSON = 1
PROTOCOL_CONTENT_TYPE_CLJ = 2

PROTOCOL_RESULT_CODE_SUCCESS = 0

class SlackerRequest(object):
    def __init__(self, ct, fname, args):
        self.ct = ct
        self.fname = fname
        self.args = args

    def serialize(self):
        serializer = json if self.ct == PROTOCOL_CONTENT_TYPE_JSON else clj
        self.args = serializer.dumps(self.args)

    def desrialize(self):
        serializer = json if self.ct == PROTOCOL_CONTENT_TYPE_JSON else clj
        self.args = serializer.loads(self.args)

class SlackerResponse(object):
    def __init__(self, ct, code, body):
        self.ct = ct
        self.code = code
        self.body = body

    def serialize(self):
        if self.body is not None:
            serializer = json if self.ct == PROTOCOL_CONTENT_TYPE_JSON else clj
            self.body = serializer.dumps(self.body)

    def desrialize(self):
        if self.body is not None:
            serializer = json if self.ct == PROTOCOL_CONTENT_TYPE_JSON else clj
            self.body = serializer.loads(self.body)

class SlackerError(object):
    def __init__(self, ct, code):
        self.ct = ct
        self.code = code

def readHeader(fd):
    """read protocol header"""
    data = fd.recv(6)
    value = struct.unpack(">bib", data)
    return value


def readRequest(fd):
    """read request body"""
    ## read content type
    ct = struct.unpack("b", fd.recv(1))[0]
    
    ## read function name
    l = struct.unpack(">H", fd.recv(2))[0]
    fname = struct.unpack(str(l)+"s", fd.recv(l))[0]
    
    ## read args body
    l = struct.unpack(">I", fd.recv(4))[0]
    args = struct.unpack(str(l)+"s", fd.recv(l))[0]

    return SlackerRequest(ct, fname, args)

def readResponse(fd):
    """read response body"""
    ## read content type
    ct = struct.unpack("b", fd.recv(1))[0]
    
    ## read result code
    rc = struct.unpack("b", fd.recv(1))[0]

    ## read body
    l = struct.unpack(">I", fd.recv(4))[0]
    if l > 0:
        body = struct.unpack(str(l)+"s", fd.recv(l))[0]
    else:
        body = None

    return SlackerResponse(ct, rc, body)

def readError(fd):
    """read error packet body"""
    rc = struct.unpack("b", fd.recv(1))

    return SlackerError(rc)

def writeHeader(fd, tid, packet_type):
    fd.write(struct.pack(">bib", PROTOCOL_VERSION, tid, packet_type))

def writeResponse(fd, resp):
    bodylen = len(resp.body)
    fd.write(struct.pack(">bbI", resp.ct, resp.rc, bodylen))
    fd.write(struct.pack(str(bodylen)+"s", resp.body))

def writeRequest(fd, req):
    fnamelen = len(req.fname)
    argslen = len(req.args)
    fd.write(struct.pack("b", req.ct))
    fd.write(struct.pack(">H"+str(fnamelen)+"s", fnamelen, req.fname))
    fd.write(struct.pack(">I"+str(argslen)+"s", argslen, req.args))


