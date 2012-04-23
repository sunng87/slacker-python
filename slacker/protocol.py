import struct
import json
import clj

PROTOCOL_VERSION = 5

PROTOCOL_HEADER = "bib"
PROTOCOL_HEADER_SIZE = 6

class SlackerRequest(object):
    type = 0
    def __init__(self, ct, fname, args):
        self.ct = ct
        self.fname = fname
        self.args = args

    def serialize(self):
        serializer = json if self.ct == 1 else clj
        self.args = serializer.dumps(self.args)

    def desrialize(self):
        serializer = json if self.ct == 1 else clj
        self.args = serializer.loads(self.args)

class SlackerResponse(object):
    type = 1
    def __init__(self, ct, code, body):
        self.ct = ct
        self.code = code
        self.body = body

    def serialize(self):
        serializer = json if self.ct == 1 else clj
        self.body = serializer.dumps(self.body)

    def desrialize(self):
        serializer = json if self.ct == 1 else clj
        self.body = serializer.loads(self.body)

class SlackerError(object):
    type = 4
    def __init__(self, ct, code):
        self.ct = ct
        self.code = code

def readHeader(fd):
    """read protocol header"""
    data = fd.read(PROTOCOL_HEADER_SIZE)
    value = struct.unpack(PROTOCOL_HEADER, data)
    return value


def readRequest(fd):
    """read request body"""
    ## read content type
    ct = struct.unpack("b", fd.read(1))
    
    ## read function name
    l = struct.unpack("H", fd.read(2))
    fname = struct.unpack("s", fd.read(l))
    
    ## read args body
    l = struct.unpack("I", fd.read(4))
    args = struct.unpack("s", fd.read(l))

    return SlackerRequest(ct, fname, args)

def readResponse(fd):
    """read response body"""
    ## read content type
    ct = struct.unpack("b", fd.read(1))
    
    ## read result code
    rc = struct.unpack("b", fd.read(1))

    ## read body
    l = struct.unpack("I", fd.read(4))
    body = struct.unpack("s", fd.read(l))

    return SlackerResponse(ct, rc, body)

def readError(fd):
    """read error packet body"""
    rc = struct.unpack("b", fd.read(1))

    return SlackerError(rc)

def writeHeader(fd, tid, packet_type):
    fd.write(struct.pack("bib", PROTOCOL_VERSION, tid, packet_type))

def writeResponse(fd, resp):
    data = struct.pack("bbIs", resp.ct, resp.rc, len(resp.body), resp.body)
    fd.write(data)

def writeRequest(fd, req):
    data = struct.pack("bHsIs", req.ct, len(req.fname),
                       req.fname, len(req.args), req.args)
    fd.write(data)


