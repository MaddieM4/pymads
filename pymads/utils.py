import struct

try:
    bytes
except:
    bytes = str

def label2str(label):
    s = struct.pack("!B", len(label))
    s += label
    return s
    
def labels2str(labels):
    s = bytes()
    for label in labels:
        s += label2str(label)
    s += struct.pack("!B", 0)
    return s

def ipstr2int(ipstr):
    ip = 0
    i = 24
    for octet in ipstr.split("."):
        ip |= (int(octet) << i)
        i -= 8
    return ip

